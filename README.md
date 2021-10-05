# xctest

A Tool for delivering squad-specific code coverage report.

# Installation

1. Execute `setup.sh` script.
2. Add `<path-to-project>/packaged/xctest/` directory to your `PATH` environment variable.<br />
Or call the script directly `venv/bin/python3 <path-to-project>/packaged/xctest/xctest.py [args]`

**And now you're ready to go.**</br>

# Usage

<h2>generate</h2>

<h3>Arguments</h3>
* -i --input | **Required**<br />
Provide an input CSV file which contains two required columns `Squad` and `Filename`.<br />
Example `squads.csv` file is present in the repository.<br />

* -p --path | **Required**<br />
Provide Xcode project workspace path.<br />

* -s --skip-tests | **Optional**<br />
Use this flag if you want to skip executing tests and generate report from last test execution results.<br />

`xctest generate -i ./squads.csv -p ~/Workspace/IBAMobileBank -s`

<h2>showreport</h2>

Show last report files.

`xctest showreport`

# Screenshots

![alt text](https://github.com/kenalizadeh/xctest/blob/master/screenshot.png)
