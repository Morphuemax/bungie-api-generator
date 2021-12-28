import os
import glob
import pprint
import shutil
import threading
import time
from functools import wraps
from multiprocessing import Process

import chevron
import timeit

from data_compiler import get_responses, get_methods, get_enums, get_models, compile_resources


def generate_enums():
    compiled_enum_data = get_enums()
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
    compiled_model_data = get_models()
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
    compiled_response_data = get_responses()
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
    compiled_api_data = get_methods()
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
    Flow = 'OAuthFlow.java'
    read_files = [HttpUtils, OAuth, ResponseObj, Flow]

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


def thread_time_decorator(thread):
    @wraps(thread)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        thread(*args, **kwargs)
        end = time.perf_counter()
        threading.current_thread().thread_duration = end - start
    return wrapper


generator_list = [generate_enums, generate_models, generate_responses, generate_api, copy_helpers]


def generate_with_threads():
    compile_resources()
    print("Generating Sources:\n")
    threadList = []
    try:
        for generator in generator_list:
            wrapped_thread = thread_time_decorator(generator)
            threadList.append(threading.Thread(target=wrapped_thread))
    except:
        print("Error Creating Thread")

    start_time = time.perf_counter()
    thread_time_map = dict()
    duration_from_decorator = 0
    for t in threadList:
        t.start()
        print(f'--- Started {t.name}')
    for t in threadList:
        t.join()
        print(f'--- Completed {t.name}')
        print(f'{t.name} took {t.thread_duration} secs ')
        duration_from_decorator += t.thread_duration
        thread_time_map[t.name] = t.thread_duration
    thread_time_map['Total sum'] = sum(thread_time_map.values())
    thread_time_map['Total No of threads'] = len(threadList)
    thread_time_map['Average thread time'] = thread_time_map['Total No of threads'] / len(threadList)

    # Capture program end time
    end_time = time.perf_counter()
    execution_time = end_time - start_time


    print(f'Total execution time: {execution_time} secs')
    print(f'Total no of threads: {len(threadList)}')
    print(f'Average time: {execution_time / len(threadList)}')
    print(f'Decorated Threads total duration: {duration_from_decorator}')
    print(f'Decorated Average: {duration_from_decorator / len(threadList)}')
    pprint.pprint(thread_time_map)
    return execution_time


def generate_without_threads():
    compile_resources()
    for generator in generator_list:
        generator()


def generate_with_mulitprocessing():
    compile_resources()
    print("Generating Sources:\n")
    processList = []
    try:
        for generator in generator_list:
            processList.append(Process(target=generator))
    except:
        print("Error Creating Thread")

    start_time = time.perf_counter()
    for t in processList:
        t.start()
        print(f'--- Started {t.name}')
    for t in processList:
        t.join()
        print(f'--- Completed {t.name}')
        print(f'{t.name} took {time.perf_counter()-start_time} secs ')

    # Capture program end time
    end_time = time.perf_counter()
    execution_time = end_time - start_time


    print(f'Total execution time: {execution_time} secs')
    return execution_time


def get_generation_times():
    starttime = timeit.default_timer()
    #print("The start time is :",starttime)
    generate_without_threads()
    generation_in_series_time = timeit.default_timer() - starttime
    generation_with_threads_time = generate_with_threads()
    # generation_with_mp_time = generate_with_mulitprocessing()
    print(f"Generation time in series: {generation_in_series_time} sec")
    print(f'Generation time multithreading: {generation_with_threads_time} sec')
    # print(f'Generation time multiprocessing: {generation_with_mp_time} sec')

    # print(f'Enum Generation Time: {timeit.timeit(generate_enums, number=1)}')
    # print(f'Model Generation Time: {timeit.timeit(generate_models, number=1)}')
    # print(f'Response Generation Time: {timeit.timeit(generate_responses, number=1)}')
    # print(f'API Generation Time: {timeit.timeit(generate_api, number=1)}')


def generate():
    # starttime = timeit.default_timer()
    generate_without_threads()
    # print(f"Generation time in series: {timeit.default_timer() - starttime} sec")
    # get_generation_times()
    # generate_with_threads()


if __name__ == '__main__':
    generate()
