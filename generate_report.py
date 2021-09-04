#!/usr/bin/python
import sys
import jinja2
import json

sys.dont_write_bytecode = True

def main(workdir, scriptdir, squad_name):
    templateLoader = jinja2.FileSystemLoader(searchpath=scriptdir)
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "template.html"
    template = templateEnv.get_template(TEMPLATE_FILE)

    data = open('{dir}/../CoverageReport/raw_report.json'.format(dir=workdir),'r')
    json_data = json.loads(data.read())

    config_data = open('{dir}/config.json'.format(dir=scriptdir))
    configs = json.loads(config_data.read())

    selected_filenames = flatten([x['filenames'] for x in configs['squads'] if x['name'] == squad_name])
    if not selected_filenames:
        selected_filenames = flatten([x['filenames'] for x in configs['squads']])

    files = []
    for target in json_data['targets']:
        for file in target['files']:
            if file['name'] in selected_filenames:
                files.append(file)

    filenames = [x['name'] for x in files]

    print('\n\u2705 DONE! Coverage report generated from {count} out of {total} files.\n'.format(count=len(files), total=len(selected_filenames)))

    missing_files = list(set(selected_filenames) - set(filenames))
    if missing_files:
        print('\u26A0\uFE0F  {count} File(s) not found:'.format(count=len(missing_files)))
        [print(' - {}'.format(x)) for x in missing_files]

    covered_lines = sum([x['coveredLines'] for x in files])

    executable_lines = sum([x['executableLines'] for x in files])

    total_coverage = covered_lines / executable_lines if executable_lines else 0

    # total_coverage = sum([x['lineCoverage'] for x in files]) / len(files)

    print('\n\033[1mTOTAL COVERAGE: {:.2%}\033[0m\n'.format(total_coverage))

    outputText = template.render(files=files, total_coverage=total_coverage)

    file = open("{dir}/../CoverageReport/report.html".format(dir=workdir), "w") 
    file.write(outputText)
    file.close()

    print("\u2139\uFE0F  Enter following command to view the report")
    print('>  open {dir}/../CoverageReport/report.html'.format(dir=workdir))

def flatten(t):
    return [item for sublist in t for item in sublist]

if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise ValueError('Working directory and script directory must be provided')
    squad = sys.argv[3] if 3 < len(sys.argv) else 'ALL'
    main(workdir=sys.argv[1], scriptdir=sys.argv[2], squad_name=squad)