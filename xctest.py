#!/usr/bin/env python

import subprocess
import argparse
import os.path
import sys
import json
import pandas as pd
import numpy as np
import shutil
from pathlib import Path

sys.dont_write_bytecode = True

# Global variables
# Appdata root directory
xctest_appdata_dir = os.path.join(os.getenv("HOME"), ".xctest")
# Logs directory
xctest_logs_dir = os.path.join(xctest_appdata_dir, 'logs')
# Derived data directory
xctest_derived_data_dir = os.path.join(xctest_appdata_dir, 'DerivedData')
# Coverage report directory
xctest_report_dir = os.path.join(xctest_appdata_dir, 'CoverageReport')
# Project directory provided by user.
project_dir = ''


def main(input_file: str):
    # Validate and load squads file
    squads_data = load_squads_file(input_file)

    run_tests()

    # Raw report json file
    raw_report_file = os.path.join(xctest_derived_data_dir, 'raw_report.json')

    # Check if raw report file exists
    if not os.path.exists(raw_report_file) and \
       not os.path.isfile(raw_report_file):
        print(
            '\n\u26A0\uFE0F  Report file is missing. \
            Please run the tests again.\n'
        )
        return

    # Open and load raw report json file
    report_data = open(raw_report_file, 'r')
    report = json.loads(report_data.read())

    # Flatten all files, remove project directory from path, remove functions
    all_files = flatten([x['files'] for x in report['targets']])
    for i in range(len(all_files)):
        all_files[i]['path'] = all_files[i]['path'].replace(
            project_dir + '/',
            ''
        )
        all_files[i].pop('functions', None)

    # Squad names listed in squads file
    squad_names = [x['name'] for x in squads_data]

    # Flat list of all squad files
    files = flatten(
        [process_files_for_squad(all_files, squads_data, x) for x in squad_names]
    )

    # Check if files are empty
    if not files:
        print('\n\u26A0\uFE0F  Could not generate report.')
        return

    # Project total coverage
    print_separator()
    print(
        '\n\u2139\uFE0F  \033[1mTOTAL COVERAGE FOR PROJECT: \
        {:.2%}\033[0m'.format(report['lineCoverage'])
    )
    print_separator()

    # Generate and save coverage report
    save_report(all_files, files)


def print_separator():
    print("\n" + "".join(['='*70]))


def flatten(t: list):
    return [item for sublist in t for item in sublist]


def load_squads_file(file):
    # Load dataframe
    df = pd.read_csv(file, sep=";")

    # Validate dataframe
    if not set(['Squad','Filename']).issubset(df.columns):
        print(
            '\n\n\u26A0\uFE0F  \033[1mInput file must be a valid csv file with following columns: \'Squad\', \'Filename\'.\033[0m\n'
        )
        sys.exit(1)
    elif df['Squad'].isnull().values.any() \
         or df['Filename'].isnull().values.any():
        print(
            '\n\n\u26A0\uFE0F  \033[1mInput file has null values.\033[0m\n'
        )
        sys.exit(1)

    # Group by squad
    df = df.groupby('Squad')

    # Merge filenames by group
    df = df['Filename'].apply(list)

    # Reset index after modifications
    df = df.reset_index()

    # Rename columns
    df.columns = ['name', 'filenames']

    # Export dataframe to json
    squads_data = df.to_json(orient='records', indent=4)

    # This part is important.
    # We have to parse json string once more because pandas.DataFrame.to_json
    # adds unnecessary escaping backlashes to path field values.
    squads_data = json.loads(squads_data)

    return squads_data


def process_files_for_squad(all_files: list, squads_data: list, squad_name: str):
    # Filenames for specified squad
    squad_filenames = flatten(
        [x['filenames'] for x in squads_data if x['name'] == squad_name]
    )

    # Check if filenames are not empty in squads file
    if not squad_filenames:
        print(
            '\n\u26A0\uFE0F  Filenames for squad {} must be provided \
            for coverage report.'.format(squad_name)
        )
        return []

    # Populate squad files
    files = []
    for file in all_files:
        # Check if any squad filename matches the file path
        if any([x in file['path'] for x in squad_filenames]):
            # Populate squad field
            file['squad'] = squad_name
            # Add file
            files.append(file)

        # Stop iterating if files matching squad filenames are all found
        if len(files) == len(squad_filenames):
            break

    print_separator()

    print(
        '\n\u2705 Done! Coverage report generated from {} out of \
        {} files for {}.\n'.format(
            len(files),
            len(squad_filenames),
            squad_name
        )
    )

    # Filenames from processed squad files
    filenames = [x for x in squad_filenames if any(
        [x in file['path'] for file in files])]

    # Make a list of squad files missing from the list of all files
    missing_files = list(set(squad_filenames) - set(filenames))

    # Report missing files
    if missing_files:
        print(
            '\u26A0\uFE0F  {count} File(s) not found:'.format(
                count=len(missing_files)
            )
        )
        [print(' - {}'.format(x)) for x in missing_files]

    # Total coverage for squad files
    squad_total_coverage = total_coverage(files)

    # Populate squad coverage field for each file
    for i in range(len(files)):
        files[i]['squad_total_coverage'] = squad_total_coverage

    print(
        '\n\u2139\uFE0F  \033[1mTOTAL COVERAGE FOR {}: {:.2%}\033[0m'.format(
            squad_name,
            squad_total_coverage
        )
    )

    print_separator()

    return files


def total_coverage(files: list):
    covered_lines = sum([x['coveredLines'] for x in files])
    executable_lines = sum([x['executableLines'] for x in files])

    return covered_lines / executable_lines if executable_lines else 0


def dataframe_from_files(files: list):
    # Load dataframe
    df = pd.DataFrame.from_dict(files)

    # Replace null values in column with 0
    df['lineCoverage'].fillna(0, inplace=True)

    # Format Line Coverage column as percentage
    df['lineCoverage'] = pd.Series(
        ["{0:.2f}%".format(val * 100) for val in df['lineCoverage']],
        index=df.index
    )

    return df


def dataframe_for_squad_files(files: list):
    if not files:
        return pd.DataFrame([])

    df = dataframe_from_files(files)

    # Format Squad Coverage column as percentage
    df['squad_total_coverage'] = pd.Series(
        ["{0:.2f}%".format(val * 100) for val in df['squad_total_coverage']],
        index=df.index
    )

    # Set column titles
    df.columns = ["Lines Covered", "Line Coverage", "File path", "File name",
                  "Executable Lines", "Squad", "Squad Coverage"]

    # Rearrange columns
    df = df[["Squad", "Squad Coverage", "File name", "Line Coverage",
             "Lines Covered", "Executable Lines", "File path"]]

    return df


def dataframe_for_undetermined_files(files: list):
    if not files:
        return pd.DataFrame([])

    df = dataframe_from_files(files)

    # Set column titles
    df.columns = ["Lines Covered", "Line Coverage", "File path",
                  "File name", "Executable Lines"]

    # Rearrange columns
    df = df[["File name", "Line Coverage", "Lines Covered",
             "Executable Lines", "File path"]]

    return df


def save_report(all_files: list, files: list):
    # Dataframe for squad files
    df1 = dataframe_for_squad_files(files)

    # Undetermined files
    paths = [x['path'] for x in files]
    undetermined_files = [x for x in all_files if x['path'] not in paths]

    # Dataframe for undetermined files
    df2 = dataframe_for_undetermined_files(undetermined_files)

    # Merge squad and undetermined files
    df = pd.concat([df1, df2], ignore_index=True)

    # Fix indexing to start from 1
    df.index = np.arange(1, len(df)+1)

    # Export as csv
    csv_report_path = os.path.join(xctest_report_dir, 'report.csv')
    df.to_csv(csv_report_path, na_rep='N/A')

    # Export as html
    html_report_path = os.path.join(xctest_report_dir, 'report.html')
    df.to_html(html_report_path, na_rep='N/A')

    print('\n\u2139\uFE0F  Enter following command to view coverage report \
        in CSV format.')
    print('>  open {dir}/report.csv\n'.format(dir=xctest_report_dir))
    print('\n\u2139\uFE0F  Enter following command to view coverage report in \
        HTML format.')
    print('>  open {dir}/report.html\n'.format(dir=xctest_report_dir))

    return df


def run_tests():
    # Clear DerivedData and CoverageReport directories
    dirs = [xctest_derived_data_dir, xctest_report_dir]
    valid_dirpaths = [
        x for x in dirs if os.path.exists(x) and os.path.isdir(x)]
    for dirpath in valid_dirpaths:
        shutil.rmtree(dirpath)

    # Recreate appdata directories
    setup_appdata_directory()

    workspace_file = os.path.join(project_dir, 'IBAMobileBank.xcworkspace')
    xcpretty_output = os.path.join(xctest_logs_dir, 'xcpretty_tests.html')

    # Check tuist
    if os.path.exists('{}/Project.swift'.format(project_dir)):
        print('- Generating project with Tuist...')
        tuist_generate = subprocess.Popen(
            [
            'tuist',
            'generate'
            ],
            cwd=project_dir
            )
        tuist_generate.communicate()

    print('- Running tests for ABB Mobile...')

    pipefail = subprocess.Popen(
        'set \
        -o \
        pipefail',
        shell=True
        )

    pipefail.communicate()

    xcodebuild = subprocess.Popen(
        'xcodebuild \
        test \
        -workspace {workspace_file} \
        -scheme IBAMobileBank-Production \
        -sdk iphonesimulator \
        -destination platform="iOS Simulator,name=iPhone 11 Pro" \
        -derivedDataPath {dd_path} \
        -enableCodeCoverage YES'.format(
            workspace_file=workspace_file,
            dd_path=xctest_derived_data_dir
        ),
        shell=True,
        stdout=subprocess.PIPE
        )

    xcpretty = subprocess.Popen(
        'xcpretty \
        -t \
        -s \
        -c \
        --report html \
        --output {xcpretty_output}'.format(xcpretty_output=xcpretty_output),
        shell=True,
        stdin=xcodebuild.stdout
        )

    xcodebuild.stdout.close()

    xcpretty.communicate()

    xcodebuild_returncode = xcodebuild.wait()

    # stdout, stderr = xcodebuild.communicate()

    if xcodebuild_returncode != 0:
        print('\n\n\u26A0\uFE0F  \033[1mTest execution failed. \nSee the logs for more detail.\033[0m')
        sys.exit(1)
    else:
        print('\n\u2705 Tests succeeded!.\nProcessing results...')

        raw_report_file = os.path.join(xctest_derived_data_dir, 'raw_report.json')

        xccov = subprocess.Popen(
            'xcrun xccov view \
            --report \
            --json {dd_path}/Logs/Test/*.xcresult > \
            {raw_report_file}'.format(
                dd_path=xctest_derived_data_dir,
                raw_report_file=raw_report_file
            ),
            shell=True
        )

        (stdout, stderr) = xccov.communicate()

        xccov_returncode = xccov.wait()

        if xccov_returncode != 0:
            print_separator()
            print('\n\n\u26A0\uFE0F  \033[1mXccov failed:\033[0m')
            print(stdout)
            sys.exit(1)


def setup_appdata_directory():
    # Appdata root directory
    Path(xctest_appdata_dir).mkdir(parents=True, exist_ok=True)
    # Logs directory
    Path(xctest_logs_dir).mkdir(parents=True, exist_ok=True)
    # CoverageReport directory
    Path(xctest_report_dir).mkdir(parents=True, exist_ok=True)


def setup(workdir: str):
    setup_appdata_directory()

    # Store project_dir in global variable
    global project_dir
    # Get normalized absolute path from passed parameter
    project_dir = os.path.abspath(workdir)


def dir_path(param):
    if os.path.isdir(param):
        return param
    else:
        raise NotADirectoryError(param)


def valid_csv_file(param):
    base, ext = os.path.splitext(param)
    if ext.lower() != '.csv':
        raise argparse.ArgumentTypeError('Input file must have csv extension.')
    return param


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Squad-based coverage reporting.')

    parser.add_argument('-i', '--input', dest='input_file',
                        type=valid_csv_file,
                        required=True, help='Path to input CSV file.')

    parser.add_argument('-p', '--path', dest='path', type=dir_path,
                        required=True, help='Path to workspace diretory.')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    try:
        setup(workdir=args.path)
        main(input_file=args.input_file)
    except KeyboardInterrupt:
        print("\n\033[1mXctest execution cancelled.\033[0m")
        sys.exit(0)
