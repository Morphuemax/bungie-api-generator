import json
import os
import glob
import shutil
import chevron



def compile_enum_data(data):
    all_enums = {}  # Create empty dict which we will fill and return
    for key in data:
        isEnum = False  # Assume it's not an enum until known
        if data[key].get('enum') is not None:   # Confirm that JSON has 'enum' key
            isEnum = True
        if isEnum:
            class_name = key.split('.')[-1] # Keys are formated {Tag}.{Name}
            values = []
            for value in data[key].get('x-enum-values'):    # This will give us the value, identifier and description
                numerical_value = value.get('numericValue')
                # Since Python uses "None" we need to change this identifier
                identifier = value.get('identifier') if not value.get('identifier') == "None" else "none"
                # Not every enum has a description
                description = value.get('description') if value.get('description') is not None else ""
                values.append({'numericValue': numerical_value,
                               'identifier': identifier,
                               'description': description
                               })

            enum = {'class_name': class_name,
                    'values': values
                    }
            # Name:{
            #     'class_name': Name,
            #     'values': [...]
            # }
            entry = {class_name: enum}
            all_enums.update(entry)
    return all_enums


def generate_enums(data_json):
    path = './generated-src/main/java/lib/enums/'

    files = glob.glob(path + '*', recursive=True)
    isExist = os.path.exists(path)

    # We want to clear the enums folder so we can generate a new one
    if isExist:
        try:
            shutil.rmtree(path)
        except OSError as e:
            print("Error: %s : %s" % (path, e.strerror))
    # Create empty directory
    os.makedirs(path)
    print("Cleared Enums directory")
    print("Generating Enums")
    # For each enum we are making a separate file
    for key in data_json:
        template_path = "src/main/generator/templates/enum.mustache"
        with open(template_path, 'r') as f:
            # Render enum.mustache with enum data we collected
            rendered = chevron.render(f, data_json[key])
        api_file = open(path + key + ".java", 'x')
        api_file.write(rendered)
        api_file.close()
        print(key + ".java created...")
    print("!All Enum files created!")

    "##################################################################"

def compile_api_parameters(parameter_data):
    param_json = []  # List allows us to dynamically add parameters
    imports = []     # If any parameters require enums, we will add them here for importing later
    for key in parameter_data:
        param_name = key['name']
        param_desc = key['description']
        param_type = key['schema']['type']  # The data type of the parameter: str, int, lst, ...
        in_type = key['in']     # Is is a path parameter or query parameter
        isArray = True if param_type == "array" else False  # Some query params allow multiple values
        isQuery = True if in_type == "query" else False     # Used for template formatting
        enum_reference = key['schema'].get('x-enum-reference')  # Get the enum reference, if any
        # Since not every param has an associated enum, we must split this into two lines
        enum_reference = enum_reference['$ref'] if enum_reference is not None else ""
        # Reference is formatted as: /{path}/{Tag}.{Name}
        enum_reference = enum_reference.split("/")[-1].split(".")[-1]   # Get ref name
        array_type = key['schema']['items']['type'] if param_type == "array" else ""    # Data type within array
        # We want to make sure that the inputs are the correct type
        array_assert_type = ""
        assert_type = ""

        required = True if key.get('required') is True else False   # Not every param is required for endpoint

        param_json.append({'param_name': param_name,
                           'param_desc': param_desc,
                           'param_type': param_type,
                           'in_type': in_type,
                           'array_type': array_type,
                           'isArray': isArray,
                           'isQuery': isQuery,
                           'required': required,
                           'assert_type': assert_type,
                           'array_assert_type': array_assert_type
                           })
        imports.append(enum_reference)
    return param_json, imports


def sortParams(params):
    i = len(params)-1
    # Recursive sort - Required params in front
    while i > 0:
        if params[i]['required']:
            if not params[i-1]['required']:
                temp = params[i-1]
                params[i-1] = params[i]
                params[i] = temp
                sortParams(params)
        i = i-1
    return params


def compile_api_data(data):
    all_methods = {}    # Creating a dict of dicts to split files by Tag
    for path in data:
        path_data = data[path]
        method_name = path_data['summary'].split('.')[1]    # Summary/Endpoint is formatted {Tag}.{Name}
        method_desc = path_data['description']
        # The key for further inspection is dependant on whether endpoint is get or post
        # If 'get' key doesn't exist, we know it must be 'post'
        if not (path_data.get('get') is None):
            endpoint_type = 'get'
        else:
            endpoint_type = 'post'
        endpoint_tag = path_data[endpoint_type]['tags'][0]
        # Gets endpoint params & enum imports
        param_data_unsorted, import_data = compile_api_parameters(data[path][endpoint_type].get('parameters'))
        # Python needs required method params to appear before non-required ones
        param_data = sortParams(param_data_unsorted)

        param_info = []
        # Appending each parameter to param_info
        for i in param_data:
            param_info_json = {}
            for j in i.keys():
                param_info_json.update({j: i[j]})
            last = True if i == param_data[-1] else False   # Used for template formatting
            param_info_json.update({'last': last})

            param_info.append(param_info_json)

        method_info = {"method_name": method_name,
                       "endpoint_tag": endpoint_tag,
                       'endpoint_type': endpoint_type,
                       'path': path,
                       'method_desc': method_desc,
                       'param_info': param_info}

        if endpoint_tag not in all_methods:
            entry = {
                endpoint_tag: {
                    'imports': [],
                    'methods': []
                }
            }
            all_methods.update(entry)
        all_methods[endpoint_tag]['methods'].append(method_info)
        # TODO: See if reference/model imports are needed
        for import_ref in import_data:
            if import_ref not in all_methods[endpoint_tag]['imports']:
                all_methods[endpoint_tag]['imports'].append(import_ref)
    return all_methods


def generate_api(data_json):
    path = './generated_src/main/py/lib/api/'

    files = glob.glob(path + '*', recursive=True)
    isExist = os.path.exists(path)

    # We want to clear the api folder so we can generate a new one
    if isExist:
        try:
            shutil.rmtree(path)
        except OSError as e:
            print("Error: %s : %s" % (path, e.strerror))
    # Create empty directory
    os.makedirs(path)
    print("Cleared API directory")
    print("Generating API")
    # For each tag we are making a separate file
    for key in data_json:
        template_path = "src/main/py/templates/api-class.mustache"
        with open(template_path, 'r') as f:
            # Render api.mustache with method data we collected
            rendered = chevron.render(f, data_json[key])
        # Some endpoints don't have a tag, we will lump them together in a 'Misc' file
        if key == '':
            key = 'Misc'
        api_file = open(path + key + ".py", 'x')
        api_file.write(rendered)
        api_file.close()
        print(key + ".py created...")
    print("!All API files created!")

    "#######################################################################"


def generate():
    apiFile = './api-src/openapi.json'
    with open(apiFile, encoding='utf-8') as data_file:
        rawData = json.load(data_file)
    pathData = rawData.get('paths')
    schemaData = rawData.get('components').get('schemas')

    print("Generating Sources:\n")
    compiled_enum_data = compile_enum_data(schemaData)
    compiled_api_data = compile_api_data(pathData)

    generate_enums(compiled_enum_data)
    print()
    generate_api(compiled_api_data)


if __name__ == '__main__':
    generate()
