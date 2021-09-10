# xctest

A Tool for delivering squad-specific code coverage report.

# Installation

You can execute the shell script directly or add it to your shell profile for convenience.<br />
To add xctest to your shell profile do the following:<br />

* Open your shell profile.<br />
If you're using zsh, then:<br />
`open ~/.zshrc`<br />
Or if you're using bash, then:<br />
`open ~/.bash_profile`<br />
* Add the following line somewhere in your shell profile (Don't forget to modify the correct path to the shell script).<br />
`source path/to/xctest/xctest.sh`<br />
* After adding xctest.sh source to your shell profile and reload by running following command.<br />
`. ~/.zshrc`<br />
or<br />
`. ~/.bash_profile`<br />

**And now you're ready to go.**

# Usage

You have to provide project root directory as first argument.<br />
Use `--skip-tests` flag if you want to generate coverage report without running the tests again.

To run tests and generate coverage report for all squads.<br />
`xctest ~/Workspace/IBAMobileBank`

To skip tests and generate coverage report for all squads.<br />
`xctest ~/Workspace/IBAMobileBank --skip-tests`

# Screenshots

![alt text](https://github.com/kenalizadeh/xctest/blob/master/screenshot.png)
