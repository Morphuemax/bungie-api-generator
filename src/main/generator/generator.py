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