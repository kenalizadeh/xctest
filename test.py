#!/usr/bin/python
import sys
import json

sys.dont_write_bytecode = True

def main():
    data = open('/Users/kenanalizadeh/Workspace/Snippets/raw_report.json','r')
    json_data = json.loads(data.read())

    config_data = open('./config.json')
    configs = json.loads(config_data.read())

    files = []
    filenames = []
    for target in json_data['targets']:
        for file in target['files']:
            if file['name'] in configs['filenames']:
                print('FILE FOUND: {file}'.format(file=file['name']))
                files.append(file)
                filenames.append(file['name'])

    print('✅ DONE! {count} files found'.format(count=len(files)))
    # print(filenames)
    unfound_files = list(set(configs['filenames']) - set(filenames))
    if unfound_files:
        print('⚠️  Files not found: {files}'.format(files=unfound_files))

    # coveredLines
    covered_lines = sum([x['coveredLines'] for x in files])
    print("covered_lines")
    print(covered_lines)

    # executableLines
    executable_lines = sum([x['executableLines'] for x in files])
    print("executable_lines")
    print(executable_lines)

    print('TOTAL COVERAGE: {:.2%}'.format(covered_lines / executable_lines))

if __name__ == '__main__':
    main()