#!/bin/bash

#Set the field separator to new line
IFS=$'\n'

function xctest() {
  if ! [ -z "$1" ]; then
    WORK_DIR="$1"
  fi
  if ! [ -d "$WORK_DIR" ]; then
      echo "xctest: no such directory: $WORK_DIR"
      return
  fi

  SQUAD_NAME='ALL'
  if ! [ -z "$2" ]; then
    SQUAD_NAME="$2"
  fi

  mdfind -name "generate_report.py" | while read DIR; do
      DIRNAME=$(dirname "$DIR")
      if [[ -f "$DIRNAME/template.html" ]] && [[ -f "$DIRNAME/xctest.sh" ]] && [[ -f "$DIRNAME/config.json" ]];
      then
          SCRIPT_DIR=$DIRNAME
      fi
  done

  if [ -z "$SCRIPT_DIR" ]; then
    echo -e "Scriptdir not found"
    return
  fi

  if test -f "Project.swift";
  then
    echo "Generating project file with Tuist"
    tuist generate
  fi

  WORKSPACE_FILE=$(find $WORK_DIR -maxdepth 1 -type d -name "*.xcworkspace")
  if [ -z "$WORKSPACE_FILE" ]; then
    echo -e "Workdir is invalid: $WORK_DIR\nXcode workspace not found"
    return
  fi

  # Clear build & coverage report folders
  rm -rf "$WORK_DIR/../DerivedData" --force
  rm -rf "$WORK_DIR/../CoverageReport" --force

  # Check if xcpretty is installed
  if ! command -v xcpretty &> /dev/null; then
    echo "Installing xcpretty..."
    gem install xcpretty
  fi

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
    mkdir "$WORK_DIR/../CoverageReport"
    # Run xccov with json output format
    xcrun xccov view --report --json $WORK_DIR/../DerivedData/Logs/Test/*.xcresult > $WORK_DIR/../CoverageReport/raw_report.json
    # Render html from template
    python3 "$SCRIPT_DIR/generate_report.py" $WORK_DIR $SCRIPT_DIR $SQUAD_NAME
    # Delete raw report json file
    # rm -rf "$WORK_DIR/../CoverageReport/raw_report.json" --force
    # Copy resources to coverage report directory
    cp -a "$SCRIPT_DIR/resources/." "$WORK_DIR/../CoverageReport/"
  else
    echo "🔴 Unit Tests Failed. Check the log output for more information"
  fi
}
