#!/bin/bash

function xctest() {
  if ! [ -z "$1" ]; then
    WORK_DIR="$1"
  fi
  if ! [ -d "$WORK_DIR" ]; then
      echo "xctest: no such directory: $WORK_DIR"
      return
  fi

  WORKSPACE_FILE=$(find $WORK_DIR -maxdepth 1 -type d -name "IBAMobileBank.xcworkspace")
  if [ -z "$WORKSPACE_FILE" ]; then
    echo -e "Workdir is invalid: $WORK_DIR\nXcode workspace not found"
    return
  fi

  if ! [ -z "$2" ]; then
    SCRIPT_DIR="$2"
  fi
  if ! [ -d "$SCRIPT_DIR" ]; then
      echo "xctest: no such directory: $SCRIPT_DIR"
      return
  fi

  SCRIPT_FILE=$(find $SCRIPT_DIR -maxdepth 1 -type f -name "xctest.sh")
  if [ -z "$SCRIPT_FILE" ]; then
    echo "Script directory is invalid: $SCRIPT_DIR"
    return
  fi

  if test -f "Project.swift";
  then
    echo "Generating project file with Tuist"
    tuist generate
  fi

  # Clear build & coverage report folders
  rm -rf "$WORK_DIR/../DerivedData" --force
  rm -rf "$WORK_DIR/../CoverageReport" --force

  set -o pipefail && xcodebuild \
  -workspace IBAMobileBank.xcworkspace \
  -scheme IBAMobileBank-Dev \
  -sdk iphonesimulator \
  -destination platform="iOS Simulator,name=iPhone 11 Pro" \
  -derivedDataPath "$WORK_DIR/../DerivedData" \
  -enableCodeCoverage YES \
  test | xcpretty --test -s --color

  if [[ $? == 0 ]]; then
    echo "✅ Unit Tests Passed. Good job!"
    # Create CoverageReport directory
    mkdir "$WORK_DIR/../CoverageReport"
    # Run xccov with json output format
    xcrun xccov view --report --json $WORK_DIR/../DerivedData/Logs/Test/*.xcresult > $WORK_DIR/../CoverageReport/raw_report.json
    # Render html from template
    python3 "$SCRIPT_DIR/generate_report.py" $WORK_DIR $SCRIPT_DIR
    # Delete raw report json file
    rm -rf "$WORK_DIR/../CoverageReport/raw_report.json" --force
    # Copy resources to coverage report directory
    cp -a "$SCRIPT_DIR/resources/." "$WORK_DIR/../CoverageReport/"
  else
    echo "🔴 Unit Tests Failed. Check the log output for more information"
  fi
}
