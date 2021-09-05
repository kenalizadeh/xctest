#!/usr/bin/python
import sys
import jinja2
import json

sys.dont_write_bytecode = True

def main(workdir, scriptdir, squad_name):
    def generate_report_for_squad(squad_name):
        selected_filenames = flatten([x['filenames'] for x in configs['squads'] if x['name'] == squad_name])
        if not selected_filenames:
            print('\n\u26A0\uFE0F  Filenames for squad {} must be provided for coverage report.'.format(squad_name))
            return [], 0

        files = []
        for target in json_data['targets']:
            for file in target['files']:
                if any(name in file['path'] for name in selected_filenames):
                    files.append(file)

        filenames = [x['name'] for x in files]

        print('\n\u2705 DONE! Coverage report generated from {} out of {} files for {}.\n'.format(len(files), len(selected_filenames), squad_name))

        missing_files = list(set(selected_filenames) - set(filenames))
        if missing_files:
            print('\u26A0\uFE0F  {count} File(s) not found:'.format(count=len(missing_files)))
            [print(' - {}'.format(x)) for x in missing_files]

        # covered_lines = sum([x['coveredLines'] for x in files])

        # executable_lines = sum([x['executableLines'] for x in files])

        # total_coverage = covered_lines / executable_lines if executable_lines else 0

        total_coverage = sum([x['lineCoverage'] for x in files]) / len(files)

        print('\n\033[1mTOTAL COVERAGE: {:.2%}\033[0m'.format(total_coverage))

        return files, total_coverage

    data = open('{dir}/../CoverageReport/raw_report.json'.format(dir=workdir),'r')
    json_data = json.loads(data.read())

    config_data = open('{dir}/config.json'.format(dir=scriptdir))
    configs = json.loads(config_data.read())

    squad_names = [x['name'] for x in configs['squads']]
    selected_squads = [squad_name]
    squad_found = squad_name in squad_names
    if not squad_found:
        selected_squads = squad_names

    for name in selected_squads:
        files, total_coverage = generate_report_for_squad(name)

    templateLoader = jinja2.FileSystemLoader(searchpath=scriptdir)
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "template.html"
    template = templateEnv.get_template(TEMPLATE_FILE)

    if not files and squad_found:
        print('\n\u26A0\uFE0F  Could not generate report.')
        return

    if len(selected_squads) > 1:
        files = flatten([x['files'] for x in json_data['targets']])
        total_coverage = json_data['lineCoverage']

    outputText = template.render(files=files, total_coverage=total_coverage)

    file = open("{dir}/../CoverageReport/report.html".format(dir=workdir), "w") 
    file.write(outputText)
    file.close()

    print("\n\u2139\uFE0F  Enter following command to view the report")
    print('>  open {dir}/../CoverageReport/report.html'.format(dir=workdir))

def flatten(t):
    return [item for sublist in t for item in sublist]

if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise ValueError('Working directory and script directory must be provided')
    squad = sys.argv[3] if 3 < len(sys.argv) else 'ALL'
    main(workdir=sys.argv[1], scriptdir=sys.argv[2], squad_name=squad)
