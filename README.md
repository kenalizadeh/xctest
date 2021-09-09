# xctest

A Tool for delivering squad-specific code coverage report.

# Installation

You can execute the shell script directly or add it to your shell profile for convenience.

To add xctest to your shell profile do the following:

Open your shell profile.

If you're using zsh, then:

`open ~/.zshrc`

Or if you're using bash, then:

`open ~/.bash_profile`

Add the following line somewhere in your shell profile (Don't forget to modify the correct path to the shell script).

`source path/to/xctest/xctest.sh`

After adding xctest.sh source to your shell profile and reload by running following command.

`. ~/.zshrc` 

or

`. ~/.bash_profile`

And now you're ready to go.

# Usage

You have to provide project root directory as first argument.

Use `--skip-tests` flag if you want to generate coverage report without running the tests again.

`xctest ~/Workspace/IBAMobileBank`
Will run tests and generate coverage report for all squads.

`xctest ~/Workspace/IBAMobileBank --skip-tests`
Will skip tests and generate coverage report for all squads.

# Screenshots

![alt text](https://github.com/kenalizadeh/xctest/blob/master/screenshot.png)
