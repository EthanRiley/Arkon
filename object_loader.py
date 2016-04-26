import json, re, copy, types

def get_functions_in_file(filename):
        try:
            file = open(filename).read()
        except(IOError, OSError):
            return None

        regex = re.compile("(def*\W(\w+)([\w\W]*?))(?=(def)|$)")
        functions = regex.findall(file)
        output = {}
        for i in range(0, len(functions)):
           output[functions[i][2]] = types.FunctionType(compile(functions[i][1],
               '<string>', 'exec'), globals())
        return output

def get_types(Json):
    types = {}
    for Type in Json["types"]:
        name = Type["type"]
        complete_type = Json["default"].copy()
        complete_type.update(Type)
        types[name] = complete_type
    Json.pop("types")
    return types

def load_objects(filename):
    Json = json.loads(open(filename).read())
    effect_funcs = get_functions_in_file(filename.split('.')[0] + ".py")
    types = get_types(Json)
    objects = {}
    for Type in Json:
        for instance in Json[Type]:
            print(types[Type])
            instance.update(types[Type])
            if effect_funcs != None:
                instance["effect"] = effect_funcs.setdefault(instance["type"],
                        None)

            objects[instance["name"]] = instance
    return objects
