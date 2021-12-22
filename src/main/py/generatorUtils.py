import json

type_conversion_dict = {
    "boolean": "Boolean",
    "byte": "Byte",
    "int16": "Short",
    "int32": "Integer",
    "uint32": "Long",
    "int64": "Long",
    "double": "Double",
    "string": "String",
    "date-time": "String",
    "object": "Object",
    "": "String"
}


def get_ref_name(ref):
    return ref.split("/")[-1].split(".")[-1]


def get_type(param, enum_imports=[], model_imports=[]):
    isArray = True if param.get('type') == "array" else False
    # Check if property is an enum
    param_type = json_extract(param, '$ref')
    if param_type:
        param_type = param_type[0]
        param_type = get_ref_name(param_type)
        if 'schema' in param:
            enum_imports.append(param_type)
        elif 'x-enum-reference' in param:
            enum_imports.append(param_type)
        else:
            model_imports.append(param_type)
    else:
        param_type = json_extract(param, 'format')
        if not param_type:
            param_type = json_extract(param, 'type')
        param_type = param_type[0] if param_type[0] != 'array' else param_type[1]

        # If property is not a model, convert it using dictionary
        if param_type in type_conversion_dict:
            param_type = type_conversion_dict[param_type]
        if isArray:
            param_type = param_type+"[]"
    if 'additionalProperties' in param:
        map_hash, mapof = get_as_map(param)
        param_type = "Map<%s, %s>" % (map_hash, mapof)
    return param_type, enum_imports, model_imports


def type_convert(t):
    if t in type_conversion_dict:
        t = type_conversion_dict[t]
    return t


def json_extract(obj, key):
    """Recursively fetch values from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    if k == key:
                        arr.append(v)
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    values = extract(obj, arr, key)
    return values


def get_as_map(json):
    map_of = json.get('additionalProperties').get('$ref')
    if map_of is not None:
        map_of = get_ref_name(map_of)
    else:
        map_of = json.get('additionalProperties')
        map_of = map_of.get('format') if map_of.get('format') is not None else map_of.get('type')
    map_hash = json.get('x-dictionary-key')
    map_hash = map_hash.get('format') if map_hash.get('format') is not None else map_hash.get('type')
    map_hash = type_convert(map_hash)
    map_of = type_convert(map_of)
    return map_hash, map_of


def get_path_data():
    # apiFile = './api-src/openapi.json'
    apiFile = '../../../api-src/openapi.json'
    with open(apiFile, 'r', encoding='utf-8') as data_file:
        rawData = json.load(data_file)
    return rawData.get('paths')


def get_schema_data():
    # apiFile = './api-src/openapi.json'
    apiFile = '../../../api-src/openapi.json'
    with open(apiFile, 'r', encoding='utf-8') as data_file:
        rawData = json.load(data_file)
    return rawData.get('components').get('schemas')

def get_response_data():
    # apiFile = './api-src/openapi.json'
    apiFile = '../../../api-src/openapi.json'
    with open(apiFile, 'r', encoding='utf-8') as data_file:
        rawData = json.load(data_file)
    return rawData.get('components').get('responses')


def sortParams(params):
    i = len(params) - 1
    # Recursive sort - Required params in front
    while i > 0:
        if params[i]['required']:
            if not params[i - 1]['required']:
                temp = params[i - 1]
                params[i - 1] = params[i]
                params[i] = temp
                sortParams(params)
        i = i - 1
    return params
