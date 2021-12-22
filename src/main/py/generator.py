import os
import glob
import shutil
import threading
import chevron

from py.data_compiler import compile_api_data, compile_model_data, compile_enum_data, compile_response_data
from py.generatorUtils import get_path_data, get_schema_data, get_response_data


def generate_enums():
    data = get_schema_data()
    compiled_enum_data = compile_enum_data(data)
    path = '../../../generated-src/main/java/lib/enums/'

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
    for key in compiled_enum_data:
        template_path = "./templates/enum.mustache"
        isFile = os.path.isfile(template_path)
        with open(template_path, 'r') as f:
            # Render enum.mustache with enum data we collected
            rendered = chevron.render(f, compiled_enum_data[key])
        api_file = open(path + key + ".java", 'x')
        api_file.write(rendered)
        api_file.close()
        # print(key + ".java created...")
    print("!All Enum files created!")

    "##################################################################"


def generate_models():
    data = get_schema_data()
    compiled_model_data = compile_model_data(data)
    path = '../../../generated-src/main/java/lib/models/'

    files = glob.glob(path + '*', recursive=True)
    isExist = os.path.exists(path)

    # We want to clear the 'models' folder, so we can generate a new one
    if isExist:
        try:
            shutil.rmtree(path)
        except OSError as e:
            print("Error: %s : %s" % (path, e.strerror))
    # Create empty directory
    os.makedirs(path)
    print("Cleared Models directory")
    print("Generating Models")
    # For each model we are making a separate file
    for key in compiled_model_data:
        template_path = "./templates/model-class.mustache"
        isFile = os.path.isfile(template_path)
        with open(template_path, 'r') as f:
            # Render model-class.mustache with model data we collected
            rendered = chevron.render(f, compiled_model_data[key])
        api_file = open(path + key + ".java", 'x')
        api_file.write(rendered)
        api_file.close()
        # print(key + ".java created...")
    print("!All Model files created!")

    "##################################################################"


def generate_responses():
    data = get_response_data()
    compiled_response_data = compile_response_data(data)
    path = '../../../generated-src/main/java/lib/responses/'

    files = glob.glob(path + '*', recursive=True)
    isExist = os.path.exists(path)

    # We want to clear the 'models' folder, so we can generate a new one
    if isExist:
        try:
            shutil.rmtree(path)
        except OSError as e:
            print("Error: %s : %s" % (path, e.strerror))
    # Create empty directory
    os.makedirs(path)
    print("Cleared Response directory")
    print("Generating Response")
    # For each model we are making a separate file
    for key in compiled_response_data:
        template_path = "./templates/response-class.mustache"
        isFile = os.path.isfile(template_path)
        with open(template_path, 'r') as f:
            # Render model-class.mustache with model data we collected
            rendered = chevron.render(f, compiled_response_data[key])
        api_file = open(path + key + "Response" + ".java", 'x')
        api_file.write(rendered)
        api_file.close()
        # print(key + ".java created...")
    print("!All Response files created!")

    "##################################################################"


def generate_api():
    data = get_path_data()
    compiled_api_data = compile_api_data(data)
    path = '../../../generated-src/main/java/lib/api/'

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
    for key in compiled_api_data:
        template_path = "./templates/api-class.mustache"
        with open(template_path, 'r') as f:
            # Render api.mustache with method data we collected
            rendered = chevron.render(f, compiled_api_data[key])

        api_file = open(path + key + ".java", 'x')
        api_file.write(rendered)
        api_file.close()
        # print(key + ".java created...")
    print("!All API files created!")

    "#######################################################################"


def copy_helpers():
    helpers_folder_path = '../java/Helpers/'
    write_path = '../../../generated-src/main/java/Helpers/'
    HttpUtils = 'HttpUtils.java'
    OAuth = 'OAuth.java'
    ResponseObj = 'ResponseObject.java'
    read_files = [HttpUtils, OAuth, ResponseObj]

    isExist = os.path.exists(write_path)

    # We want to clear the api folder so we can generate a new one
    if isExist:
        try:
            shutil.rmtree(write_path)
        except OSError as e:
            print("Error: %s : %s" % (write_path, e.strerror))
    # Create empty directory
    os.makedirs(write_path)

    for file in read_files:
        src_file = helpers_folder_path + file
        dest_file = write_path + file
        src_file = open(src_file, 'r')
        dest_file = open(dest_file, 'x')
        shutil.copyfileobj(src_file, dest_file)
        # print("Copied " + file)
    print("!All Helpers Copied")

    "#####################################################################"


def generate():
    generator_list = [generate_enums, generate_models, generate_responses, generate_api, copy_helpers]
    print("Generating Sources:\n")
    try:
        for generator in generator_list:
            threading.Thread(target=generator).start()
    except:
        print("Error Creating Thread")


if __name__ == '__main__':
    generate()
