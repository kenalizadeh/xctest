#!/usr/bin/python
import sys
import json
import pandas as pd
import numpy as np

sys.dont_write_bytecode = True

def main(workdir, scriptdir, squad_name):
    def generate_report_for_squad(squad_name):
        selected_filenames = flatten([x['filenames'] for x in configs['squads'] if x['name'] == squad_name])
        if not selected_filenames:
            print('\n\u26A0\uFE0F  Filenames for squad {} must be provided for coverage report.'.format(squad_name))
            return []

        files = []
        for file in flatten([x['files'] for x in json_data['targets']]):
            if any([x in file['path'] for x in selected_filenames]):
                file['squad'] = squad_name
                file.pop('functions', None)
                files.append(file)

        filenames = [x for x in selected_filenames if any([x in file['path'] for file in files])]

        print('\n\u2705 DONE! Coverage report generated from {} out of {} files for {}.\n'.format(len(files), len(selected_filenames), squad_name))

        missing_files = list(set(selected_filenames) - set(filenames))
        if missing_files:
            print('\u26A0\uFE0F  {count} File(s) not found:'.format(count=len(missing_files)))
            [print(' - {}'.format(x)) for x in missing_files]

        print('\n\033[1mTOTAL COVERAGE: {:.2%}\033[0m'.format(total_coverage(files)))

        return files

    data = open('{dir}/../DerivedData/raw_report.json'.format(dir=workdir),'r')
    json_data = json.loads(data.read())

    config_data = open('{dir}/config.json'.format(dir=scriptdir))
    configs = json.loads(config_data.read())

    squad_names = [x['name'] for x in configs['squads']]
    selected_squads = [squad_name]
    squad_found = squad_name in squad_names
    if not squad_found:
        selected_squads = squad_names

    files = flatten([generate_report_for_squad(x) for x in selected_squads])

    if not files and squad_found:
        print('\n\u26A0\uFE0F  Could not generate report.')
        return

    save_report(workdir, scriptdir, files)

    print("\n\u2139\uFE0F  Enter following command to view the report")
    print('>  open {dir}/../CoverageReport/report.html'.format(dir=workdir))

def flatten(t):
    return [item for sublist in t for item in sublist]

def total_coverage(files):
    covered_lines = sum([x['coveredLines'] for x in files])
    executable_lines = sum([x['executableLines'] for x in files])
    # total_coverage = sum([x['lineCoverage'] for x in files]) / len(files)
    return covered_lines / executable_lines if executable_lines else 0

def save_report(workdir, scriptdir, files):
    pretty_json = json.dumps(files, indent=4, sort_keys=True)

    file = open("{dir}/../CoverageReport/report.json".format(dir=workdir), "w") 
    file.write(pretty_json)
    file.close()

    df = pd.DataFrame.from_dict(files)
    df['lineCoverage'] = pd.Series(["{0:.2f}%".format(val * 100) for val in df['lineCoverage']], index = df.index)
    df.columns = ["Lines Covered", "Executable Lines", "Line Coverage", "File name", "File path", "Squad"]
    df = df[["Squad", "File name", "Line Coverage", "Lines Covered", "Executable Lines", "File path"]]
    df.index = np.arange(1, len(df)+1)
    df.to_csv("{dir}/../CoverageReport/report.csv".format(dir=workdir))
    df.to_html("{dir}/../CoverageReport/report.html".format(dir=workdir))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise ValueError('Working directory and script directory must be provided')
    squad = sys.argv[3] if 3 < len(sys.argv) else 'ALL'
    main(workdir=sys.argv[1], scriptdir=sys.argv[2], squad_name=squad)
