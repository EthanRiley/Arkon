import json, re, copy, types

def get_functions_in_file(filename):
        try:
            file = open(filename).read()
        except(IOError, OSError):
            return None

        regex = re.compile("(def*\W(\w+)([\w\W]*?))(?=(def)|$)")
        functions = regex.findall(file)
        output = {}
        for i in len(functions):
           output[functions[2][i]] = types.FunctionType(compile(functions[1][i],
               '<string>', 'exec'), globals())
        return output

def get_types(self, json):
    types = {}
    for Type in json["types"]:
        name = Type.name
        Type.pop("name")
        complete_type = json["default"].copy()
        complete_type.update(Type)
        types["name"] = complete_type

    json.pop("types")
    return types

def load_objects(self, filename):
    json = json.loads(open(filename).read())
    effect_funcs = get_functions_in_file(filename.split('.')[0] + ".py")
    types = __get_types()
    objects = []
    for Type in self.json:
        for instance in self.json[Type]:
            instance.update(types[Type])

            if effect_funcs != None:
                instance["effect"] = effect_funcs[instance["name"]]

            objects.append(instance)
    return objects
