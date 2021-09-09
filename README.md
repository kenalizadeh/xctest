# xctest

Tool for delivering squad-specific code coverage report with html generation.

# Installation

`source path/to/xctest/xctest.sh`
After adding xctest.sh source to your shell profile, you're ready to go.

# Usage

Pass workdirectory as first argument.
Use `--skip-tests` flag if you want to generate coverage report without running the tests again.

`xctest ~/Workspace/IBAMobileBank`
Will run tests and generate coverage report for all squads.

`xctest ~/Workspace/IBAMobileBank --skip-tests`
Will skip tests and generate coverage report for all squads.

# Screenshots

![alt text](https://github.com/kenalizadeh/xctest/blob/master/screenshot.png)
