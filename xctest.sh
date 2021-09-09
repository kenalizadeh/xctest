#!/bin/bash

function xctest() {
  if ! [ -z "$1" ]; then
    WORK_DIR="$1"
  fi
  if ! [ -d "$WORK_DIR" ]; then
      echo "xctest: no such directory: $WORK_DIR"
      return
  fi

  mdfind -name "generate_report.py" | while read DIR; do
      DIRNAME=$(dirname "$DIR")
      if [[ -f "$DIRNAME/requirements.txt" ]] && [[ -f "$DIRNAME/xctest.sh" ]] && [[ -f "$DIRNAME/config.json" ]];
      then
          SCRIPT_DIR=$DIRNAME
      fi
  done

  if [ -z "$SCRIPT_DIR" ]; then
    echo -e "Scriptdir not found"
    return
  fi

  WORKSPACE_FILE=$(find $WORK_DIR -maxdepth 1 -type d -name "*.xcworkspace")
  if [ -z "$WORKSPACE_FILE" ]; then
    echo -e "Workdir is invalid: $WORK_DIR\nXcode workspace not found"
    return
  fi

  if [ $2 != "--skip-tests" ];
  then
    if test -f "$WORK_DIR/Project.swift";
    then
      echo "Generating project file with Tuist"
      tuist generate --path $WORK_DIR
    fi

    # Clear build & coverage report folders
    rm -rf "$WORK_DIR/../DerivedData" --force
    rm -rf "$WORK_DIR/../CoverageReport" --force

    # Check if xcpretty is installed
    if ! command -v xcpretty &> /dev/null; then
      echo "Installing xcpretty..."
      gem install xcpretty
    fi

    echo "- Running tests for $(basename $WORKSPACE_FILE)..."

    set -o pipefail && xcodebuild \
    -workspace $WORKSPACE_FILE \
    -scheme IBAMobileBank-Production \
    -sdk iphonesimulator \
    -destination platform="iOS Simulator,name=iPhone 11 Pro" \
    -derivedDataPath "$WORK_DIR/../DerivedData" \
    -enableCodeCoverage YES \
    test | xcpretty --test -s --color

    if [[ $? == 0 ]]; then
      echo "✅ Unit Tests Passed. Good job!"
      # Create CoverageReport directory
      mkdir -p "$WORK_DIR/../CoverageReport"
      # Run xccov with json output format
      xcrun xccov view --report --json $WORK_DIR/../DerivedData/Logs/Test/*.xcresult > $WORK_DIR/../DerivedData/raw_report.json
    else
      echo "🔴 Unit Tests Failed. Check the log output for more information"
      return 1 2>/dev/null
    fi
  else
    echo "- Skipped tests for $WORKSPACE_FILE_NAME..."
  fi

  # Install python requirements
  pip3 install -r requirements.txt
  # Render html from template
  python3 "$SCRIPT_DIR/generate_report.py" $WORK_DIR $SCRIPT_DIR
}
