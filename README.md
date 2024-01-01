## :no_entry: [DEPRECATED] Active at https://github.com/kenalizadeh/xctest_rs

# xctest

A Tool for delivering squad-specific code coverage report with Pandas.

# Installation

1. Execute `setup.sh` script.
2. Add `<path-to-project>/packaged/xctest/` directory to your `PATH` environment variable and reload your shell<br />
Then you can use xctest from everywhere<br />

Or use the script directly `venv/bin/python3 <path-to-project>/packaged/xctest/xctest.py [args]`

**And now you're ready to go.**</br>

# Usage

<h2>xctest run [args]</h2></br>
Run tests and generate coverage report from results.

* -i --input | **Required**<br />
Provide an input CSV file which contains two required columns `Squad` and `Filename`.<br />
Example `squads.csv` file is present in the repository.<br />

* -p --path | **Required**<br />
Provide Xcode project workspace path.<br />
<h2>xctest generate [args]</h2></br>
Generate coverage report from provided test results.

* -i --input | **Required**<br />
Provide an input `.csv` file which contains two required columns `Squad` and `Filename`.<br />
Example `squads.csv` file is present in the repository.<br />

* -f --file | **Required**<br />
Provide an input `.xcresult` file.<br />
<h2>xctest showreport</h2>
Show reports from last generate execution.

# Screenshots

![alt text](https://github.com/kenalizadeh/xctest/blob/master/screenshot.png)
