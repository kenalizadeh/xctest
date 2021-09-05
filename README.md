# xctest

Tool for delivering squad-specific code coverage report with html generation.

# Installation

After adding xctest.sh source to your shell profile, you're ready to go.

# Usage

Pass workdirectory as first argument.
Squad name is optional. If not provided report will be generated for all squad listed in config file.
Use `--skip-tests` flag if you want to generate coverage report without running the tests again.

`xctest ~/Workspace/IBAMobileBank`
Will run tests and generate coverage report for all squads.

`xctest ~/Workspace/IBAMobileBank ADS`
Will run tests and generate coverage report for ADS squad.

`xctest ~/Workspace/IBAMobileBank --skip-tests`
Will skip tests and generate coverage report for all squads.

`xctest ~/Workspace/IBAMobileBank ADS --skip-tests`
Will skip tests and generate coverage report for ADS squad.

# Screenshots
