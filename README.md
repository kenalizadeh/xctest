# xctest

A Tool for delivering squad-specific code coverage report.

# Installation

1. Execute `setup.sh` script.
2. Add `<path-to-project>/packaged/xctest/` directory to your `PATH`.

**And now you're ready to go.**</br>

# Usage

* -i --input Path to input CSV file<br />
Provide an input CSV file which contains two required columns `Squad` and `Filename`. Example `squads.csv` file is present in the repository.<br />

* -p --path  Path to workspace diretory.<br />
Provide Xcode project workspace path.<br />

`xctest -i ./squads.csv -p ~/Workspace/IBAMobileBank`

# Screenshots

![alt text](https://github.com/kenalizadeh/xctest/blob/master/screenshot.png)
