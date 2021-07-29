#!/usr/bin/python
import sys
import jinja2
import json

sys.dont_write_bytecode = True

def main(scriptdir, workdir):
    templateLoader = jinja2.FileSystemLoader(searchpath=scriptdir)
    print('workdir', workdir)
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "template.html"
    template = templateEnv.get_template(TEMPLATE_FILE)

    data = open('{dir}/../CoverageReport/raw_report.json'.format(dir=workdir),'r')
    json_data = json.loads(data.read())

    outputText = template.render(data=json_data)

    print(outputText)

    file = open("{dir}/../CoverageReport/report.html".format(dir=workdir), "w") 
    file.write(outputText)
    file.close()

    print("✅ Code coverage report generated!")
    print("Enter following command to view the report")
    print('open "{dir}/../CoverageReport/report.html"'.format(dir=workdir))

if __name__ == '__main__':
    main(workdir=sys.argv[1], scriptdir=sys.argv[2])