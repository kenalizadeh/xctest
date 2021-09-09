#!/usr/bin/python
import os.path
import sys
import json
import pandas as pd
import numpy as np

sys.dont_write_bytecode = True

def main(workdir, scriptdir):
    # Normalize workdir
    workdir = os.path.normpath(workdir)

    # Open and load raw report json file
    data = open('{dir}/../DerivedData/raw_report.json'.format(dir=workdir),'r')
    json_data = json.loads(data.read())

    # Open and load config file
    config_data = open('{dir}/config.json'.format(dir=scriptdir))
    configs = json.loads(config_data.read())

    # Flatten all files, remove workdir from path, remove functions
    all_files = flatten([x['files'] for x in json_data['targets']])
    for i in range(len(all_files)):
        all_files[i]['path'] = all_files[i]['path'].replace(workdir, '')
        all_files[i].pop('functions', None)

    # Squad names listed in config file
    squad_names = [x['name'] for x in configs['squads']]

    # Flat list of all squad files
    files = flatten([process_files_for_squad(all_files, configs, x) for x in squad_names])

    # Check if files are empty
    if not files:
        print('\n\u26A0\uFE0F  Could not generate report.')
        return

    # Generate and save coverage report
    save_report(workdir, all_files, files)

def flatten(t):
    return [item for sublist in t for item in sublist]

def process_files_for_squad(all_files, configs, squad_name):
    # Filenames for specified squad
    selected_filenames = flatten([x['filenames'] for x in configs['squads'] if x['name'] == squad_name])

    # Check if filenames are not empty in config file
    if not selected_filenames:
        print('\n\u26A0\uFE0F  Filenames for squad {} must be provided for coverage report.'.format(squad_name))
        return []

    # Populate squad files
    files = []
    for file in all_files:
        # Check if any squad filename matches the file path
        if any([x in file['path'] for x in selected_filenames]):
            # Populate squad field
            file['squad'] = squad_name
            # Add file
            files.append(file)

        # Stop iterating if files matching squad filenames are all found
        if len(files) >= len(selected_filenames) / 2:
            break

    print('\n======================================================================')

    print('\n\u2705 Done! Coverage report generated from {} out of {} files for {}.\n'.format(len(files), len(selected_filenames), squad_name))

    # Filenames from processed squad files
    filenames = [x for x in selected_filenames if any([x in file['path'] for file in files])]

    # Make a list of squad files missing from the list of all files
    missing_files = list(set(selected_filenames) - set(filenames))

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

def dataframe_for_squad_files(files):
    # Load dataframe
    df = pd.DataFrame.from_dict(files)

    # Format Line Coverage column as percentage
    df['lineCoverage'] = pd.Series(["{0:.2f}%".format(val * 100) for val in df['lineCoverage']], index = df.index)

    # Format Squad Coverage column as percentage
    df['squad_total_coverage'] = pd.Series(["{0:.2f}%".format(val * 100) for val in df['squad_total_coverage']], index = df.index)

    # Set column titles
    df.columns = ["Lines Covered", "Line Coverage", "File path", "File name", "Executable Lines", "Squad", "Squad Coverage"]

    # Rearrange columns
    df = df[["Squad", "Squad Coverage", "File name", "Line Coverage", "Lines Covered", "Executable Lines", "File path"]]

    return df

def dataframe_for_undetermined_files(files):
    # Load dataframe
    df = pd.DataFrame.from_dict(files)
    
    # Format Line Coverage column as percentage
    df['lineCoverage'] = pd.Series(["{0:.2f}%".format(val * 100) for val in df['lineCoverage']], index = df.index)

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

    print("\n\u2139\uFE0F  Enter following command to view coverage report.")
    print('>  open {dir}/report.csv'.format(dir=report_path))
    print('>  open {dir}/report.html\n'.format(dir=report_path))

    return df

if __name__ == '__main__':
    main(workdir=sys.argv[1], scriptdir=sys.argv[2])
