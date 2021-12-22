from py.generatorUtils import type_conversion_dict, get_ref_name, get_type, sortParams


def compile_enum_data(data):
    all_enums = {}  # Create empty dict which we will fill and return
    for k in data:
        isEnum = False  # Assume it's not an enum until known
        if data[k].get('enum') is not None:  # Confirm that JSON has 'enum' key
            isEnum = True
        if isEnum:
            class_name = k.split('.')[-1]  # Keys are formated {Tag}.{Name}
            values = []
            enum_type = data[k].get('format')
            if enum_type in type_conversion_dict:
                enum_type = type_conversion_dict[enum_type]
            for value in data[k].get('x-enum-values'):  # This will give us the value, identifier and description
                numerical_value = value.get('numericValue')
                identifier = value.get('identifier')
                # Not every enum has a description
                description = value.get('description') if value.get('description') is not None else ""
                values.append({'numericValue': numerical_value,
                               'identifier': identifier,
                               'description': description
                               })

            enum = {'class_name': class_name,
                    'enum_type': enum_type,
                    'values': values
                    }
            # Name:{
            #     'class_name': Name,
            #     'values': [...]
            # }
            entry = {class_name: enum}
            all_enums.update(entry)
    return all_enums

    "############################################################"


def compile_model_data(data):
    all_models = {}
    for k in data:
        enums = []
        models = []
        isResponse = False
        if data[k].get('type') == "object":  # Model is defined by having object type
            isResponse = True
        if isResponse:
            class_name = get_ref_name(k)  # Get ref name
            all_properties = []
            model_properties = data[k].get('properties')
            property_name = ""
            if model_properties is None:
                model_properties = {k: data[k]}
            for k2 in model_properties:
                if model_properties is not None:
                    model_property = model_properties[k2]
                    property_name = get_ref_name(k2)
                    property_type, isArray, enums, models = get_type(model_property, enums, models)
                all_properties.append({
                    'property_type': property_type,
                    'property_name': property_name,
                    'Property_Name': property_name[0].upper() + property_name[1:],
                    'isArray': isArray,
                    'isRequest': True if "Request" in class_name else False
                })
                # Each entry corresponds to a separate model
                entry = {
                    class_name: {
                        'imports': {
                            'enums': enums,
                            'models': models
                        },
                        'properties': all_properties,
                        'class_name': class_name
                    }
                }
                all_models.update(entry)
    return all_models

    "############################################################"


def compile_api_parameters(parameter_data):
    param_json = []  # List allows us to dynamically add parameters
    enums = []  # If any parameters require enums, we will add them here for importing later
    has_query = False
    for key in parameter_data:
        param_name = key['name']
        param_desc = key['description']
        # type = key['schema']['type']  # The data type of the parameter: str, int, lst, ...
        param_type, isArray, enums, models = get_type(key, enums)
        in_type = key['in']  # Is "in" a path parameter or query parameter
        isQuery = True if in_type == "query" else False  # Used for template formatting

        required = True if key.get('required') is True else False  # Not every param is required for endpoint

        param_json.append({'param_name': param_name,
                           'param_desc': param_desc,
                           'param_type': param_type,
                           'in_type': in_type,
                           'isArray': isArray,
                           'isQuery': isQuery,
                           'required': required
                           })
        if isQuery:
            has_query = True
    return param_json, enums, has_query

    "#############################################"


def compile_api_data(data):
    all_methods = {}  # Creating a dict of dicts to split files by Tag
    for path in data:
        path_data = data[path]
        method_name = path_data['summary'].split('.')[1]  # Summary/Endpoint is formatted {Tag}.{Name}
        method_desc = path_data['description']
        # The key for further inspection is dependent on whether endpoint is get or post
        # If 'get' key doesn't exist, we know it must be 'post'
        if not (path_data.get('get') is None):
            endpoint_type = 'get'
        else:
            endpoint_type = 'post'
        isPost = True if endpoint_type == 'post' else False
        endpoint_tag = path_data[endpoint_type]['tags'][0]
        # Gets endpoint params & enum imports
        param_data_unsorted, import_data, has_query = compile_api_parameters(
            data[path][endpoint_type].get('parameters'))
        # Python needs required method params to appear before non-required ones
        param_data = sortParams(param_data_unsorted)

        param_info = []
        # Appending each parameter to param_info
        for i in param_data:
            param_info_json = {}
            for j in i.keys():
                param_info_json.update({j: i[j]})
            last = True if i == param_data[-1] else False  # Used for template formatting
            param_info_json.update({'last': last})

            param_info.append(param_info_json)

        return_type = path_data[endpoint_type]['responses']['200']['$ref']
        return_type = return_type.split("/")[-1].split(".")[-1]  # Get ref name

        if type_conversion_dict.get(return_type) is not None:
            return_type = type_conversion_dict.get(return_type)

        request_type = path_data[endpoint_type].get('requestBody')
        request_type = request_type['content']['application/json']['schema'] if request_type is not None else ""

        if request_type != "":
            if request_type.get('$ref') is not None:
                request_type = request_type['$ref']
                request_type = get_ref_name(request_type)
            else:
                request_type = request_type['items']['format']
                request_type = type_conversion_dict.get(request_type)

        method_info = {"method_name": method_name,
                       "endpoint_tag": endpoint_tag,
                       'endpoint_type': endpoint_type,
                       'isPost': isPost,
                       'path': path,
                       'method_desc': method_desc,
                       'param_info': param_info,
                       'request_type': request_type,
                       'return_type': return_type,
                       'has_query': has_query
                       }

        if endpoint_tag not in all_methods:
            entry = {
                endpoint_tag: {
                    'imports': {
                        'enums': [],
                        'models': [],
                        'responses': []
                    },
                    "tag": endpoint_tag,
                    'methods': []
                }
            }
            all_methods.update(entry)
        all_methods[endpoint_tag]['methods'].append(method_info)
        # Grab/Add enums needed for parameters to imports
        for import_ref in import_data:
            # Check if enum is already imported
            if import_ref not in all_methods[endpoint_tag]['imports']['enums']:
                all_methods[endpoint_tag]['imports']['enums'].append(import_ref)
        # Add model of RequestBody to imports
        if request_type != "":
            # Check if model is already imported
            if request_type not in all_methods[endpoint_tag]['imports']['models']:
                if request_type not in type_conversion_dict.values():
                    all_methods[endpoint_tag]['imports']['models'].append(request_type)
        # Add model of the return type to imports
        # Check if model is already imported
        if return_type not in all_methods[endpoint_tag]['imports']['models']:
            if return_type not in type_conversion_dict.values():
                all_methods[endpoint_tag]['imports']['responses'].append(return_type)
    return all_methods