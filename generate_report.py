#!/usr/bin/python
import subprocess
import argparse
import os.path
import sys
import json
import pandas as pd
import numpy as np
import shutil

sys.dont_write_bytecode = True

def main(workdir, skip_tests, output_path):
    # Get full path to xctest
    scriptdir = os.path.dirname(os.path.abspath(__file__))

    # Normalize workdir
    workdir = os.path.abspath(workdir)

    if not skip_tests:
        run_tests(workdir)

    raw_report_file = '{dir}/../DerivedData/raw_report.json'.format(dir=workdir)

    # Check if raw report file exists
    if not os.path.exists(raw_report_file) and not os.path.isfile(raw_report_file):
        print('\n\u26A0\uFE0F  Report file is missing. Please run the tests again.\n')
        return

    # Open and load raw report json file
    report_data = open(raw_report_file,'r')
    report = json.loads(report_data.read())

    # Squad config file
    configs = load_squad_configs(scriptdir)

    # Flatten all files, remove workdir from path, remove functions
    all_files = flatten([x['files'] for x in report['targets']])
    for i in range(len(all_files)):
        all_files[i]['path'] = all_files[i]['path'].replace(workdir + '/', '')
        all_files[i].pop('functions', None)

    # Squad names listed in config file
    squad_names = [x['name'] for x in configs]

    # Flat list of all squad files
    files = flatten([process_files_for_squad(all_files, configs, x) for x in squad_names])

    # Check if files are empty
    if not files:
        print('\n\u26A0\uFE0F  Could not generate report.')
        return

    # Project total coverage
    print('\n======================================================================')
    print('\n\u2139\uFE0F  \033[1mTOTAL COVERAGE FOR PROJECT: {:.2%}\033[0m'.format(report['lineCoverage']))
    print('\n======================================================================\n')

    # Generate and save coverage report
    save_report(workdir, all_files, files)

def flatten(t):
    return [item for sublist in t for item in sublist]

def load_squad_configs(scriptdir):
    # Load dataframe
    df = pd.read_csv('{dir}/squads.csv'.format(dir=scriptdir), sep=";")

    # Group by squad
    df = df.groupby('Squad')

    # Merge filenames by group
    df = df['Filename'].apply(list)

    # Reset index after modifications
    df = df.reset_index()

    # Rename columns
    df.columns = ['name', 'filenames']

    # Export dataframe to json
    configs = df.to_json(orient='records', indent=4)

    # This part is important.
    # We have to parse json string once more because pandas.DataFrame.to_json adds unnecessary escaping backlashes to path field values.
    configs = json.loads(configs)

    return configs

def process_files_for_squad(all_files, configs, squad_name):
    # Filenames for specified squad
    squad_filenames = flatten([x['filenames'] for x in configs if x['name'] == squad_name])

    # Check if filenames are not empty in config file
    if not squad_filenames:
        print('\n\u26A0\uFE0F  Filenames for squad {} must be provided for coverage report.'.format(squad_name))
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

    print('\n======================================================================')

    print('\n\u2705 Done! Coverage report generated from {} out of {} files for {}.\n'.format(len(files), len(squad_filenames), squad_name))

    # Filenames from processed squad files
    filenames = [x for x in squad_filenames if any([x in file['path'] for file in files])]

    # Make a list of squad files missing from the list of all files
    missing_files = list(set(squad_filenames) - set(filenames))

    # Report missing files
    if missing_files:
        print('\u26A0\uFE0F  {count} File(s) not found:'.format(count=len(missing_files)))
        [print(' - {}'.format(x)) for x in missing_files]

    # Total coverage for squad files
    squad_total_coverage = total_coverage(files)

    # Populate squad coverage field for each file
    for i in range(len(files)):
        files[i]['squad_total_coverage'] = squad_total_coverage

    print('\n\u2139\uFE0F  \033[1mTOTAL COVERAGE FOR {}: {:.2%}\033[0m'.format(squad_name, squad_total_coverage))

    print('\n======================================================================')

    return files

def total_coverage(files):
    covered_lines = sum([x['coveredLines'] for x in files])
    executable_lines = sum([x['executableLines'] for x in files])

    return covered_lines / executable_lines if executable_lines else 0

def dataframe_from_files(files):
    # Load dataframe
    df = pd.DataFrame.from_dict(files)

    # Replace null values in column with 0
    df['lineCoverage'].fillna(0, inplace=True)

    # Format Line Coverage column as percentage
    df['lineCoverage'] = pd.Series(["{0:.2f}%".format(val * 100) for val in df['lineCoverage']], index = df.index)

    return df

def dataframe_for_squad_files(files):
    if not files:
        return pd.DataFrame([])

    df = dataframe_from_files(files)

    # Format Squad Coverage column as percentage
    df['squad_total_coverage'] = pd.Series(["{0:.2f}%".format(val * 100) for val in df['squad_total_coverage']], index = df.index)

    # Set column titles
    df.columns = ["Lines Covered", "Line Coverage", "File path", "File name", "Executable Lines", "Squad", "Squad Coverage"]

    # Rearrange columns
    df = df[["Squad", "Squad Coverage", "File name", "Line Coverage", "Lines Covered", "Executable Lines", "File path"]]

    return df

def dataframe_for_undetermined_files(files):
    if not files:
        return pd.DataFrame([])

    df = dataframe_from_files(files)

    # Set column titles
    df.columns = ["Lines Covered", "Line Coverage", "File path", "File name", "Executable Lines"]

    # Rearrange columns
    df = df[["File name", "Line Coverage", "Lines Covered", "Executable Lines", "File path"]]

    return df

def save_report(workdir, all_files, files):
    # Dataframe for squad files
    df1 = dataframe_for_squad_files(files)

    # Undetermined files
    undetermined_files = [x for x in all_files if x['path'] not in [x['path'] for x in files]]

    # Dataframe for undetermined files
    df2 = dataframe_for_undetermined_files(undetermined_files)

    # Merge squad and undetermined files
    df = pd.concat([df1, df2], ignore_index=True)

    # Fix indexing to start from 1
    df.index = np.arange(1, len(df)+1)

    # Path for report output files
    report_path = os.path.normpath('{dir}/../CoverageReport/'.format(dir=workdir))

    # Export as csv
    df.to_csv("{dir}/report.csv".format(dir=report_path), na_rep='N/A')

    # Export as html
    df.to_html("{dir}/report.html".format(dir=report_path), na_rep='N/A')

    print("\n\u2139\uFE0F  Enter following command to view coverage report in CSV format.")
    print('>  open {dir}/report.csv\n'.format(dir=report_path))
    print("\n\u2139\uFE0F  Enter following command to view coverage report in HTML format.")
    print('>  open {dir}/report.html\n'.format(dir=report_path))

    return df

def run_tests(workdir):
    dirpaths = [os.path.normpath("{workdir}/../{dir}".format(workdir=workdir, dir=x)) for x in ('DerivedData', 'CoverageReport')]
    dirpaths = [x for x in dirpaths if os.path.exists(x) and os.path.isdir(x)]
    for dirpath in dirpaths:
        shutil.rmtree(dirpath)

    workspace_file = "{dir}/IBAMobileBank.xcworkspace".format(dir=workdir)
    derived_path = '{dir}/../DerivedData'.format(dir=workdir)
    xcpretty_output = os.path.normpath('{dir}/../DerivedData/xcpretty_tests.html'.format(dir=workdir))

    print('- Running tests for ABB Mobile...')

    command = 'set -o pipefail && xcodebuild \
            -workspace {workspace_file} \
            -scheme IBAMobileBank-Production \
            -sdk iphonesimulator \
            -destination platform="iOS Simulator,name=iPhone 11 Pro" \
            -derivedDataPath {derived_path} \
            -enableCodeCoverage YES \
            test | xcpretty \
            --test \
            -s \
            --color \
            --report html \
            --output {xcpretty_output}'.format(workspace_file=workspace_file, derived_path=derived_path, xcpretty_output=xcpretty_output)

    result = subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL)

    if result.returncode != 0:
        log_output = ''
        print('\n\u26A0\uFE0F  Test execution failed\nSee logs at: {}\n'.format(log_output))
        print(result.output[:, -30])
        sys.exit(1)

def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

def valid_csv_file(param):
    base, ext = os.path.splitext(param)
    if ext.lower() != '.csv':
        raise argparse.ArgumentTypeError('Input file must have csv extension.')
    return param

def parse_arguments():
    parser = argparse.ArgumentParser(description='Squad-based coverage reporting.')
    parser.add_argument('-i', '--input_file', type=valid_csv_file, required=True, help='Path to input CSV file.')
    parser.add_argument('-p', '--path', type=dir_path, required=True, help='Path to workspace diretory.')
    parser.add_argument('-s', '--skip-tests', dest='skip_tests', action='store_true', required=False, help='Skips tests and generates coverage report from last test results.')
    parser.add_argument('-o', '--output', dest='output_path', type=dir_path, required=True, help='Path for report output.')

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    try:
        main(workdir=args.path, skip_tests=args.skip_tests, output_path=args.output_path)
    except KeyboardInterrupt:
        print("\nXctest execution cancelled.")
        sys.exit(0)
