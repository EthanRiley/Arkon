import json, re, copy, types

def get_functions_in_file(filename):
        file = open(filename).read()
        regex = re.compile("(def*\W(\w+)([\w\W]*?))(?=(def)|$)")
        functions = regex.findall(file)
        output = {}
        for i in len(functions):
           output[functions[2][i]] = types.FunctionType(compile(functions[1][i],
               '<string>', 'exec'), globals())
        return output

class object_loader:

    def __init__(self, filename):
      self.json = json.loads(open(filename).read())
      self.effect_funcs = get_functions_in_file("game_objects.py")

    def __get_types(self):
        types = {}
        for Type in self.json["types"]:
            name = Type.name
            Type.pop("name")
            complete_type = self.json["default"].copy()
            complete_type.update(Type)
            types["name"] = complete_type

        self.json.pop("types")
        return types

    def load(self):
        types = self.__get_types()
        objects = []
        for Type in self.json:
            for instance in self.json[Type]:
                instance.update(types[Type])
                instance["effect"] = self.effect_funcs[instance["name"]]
                objects.append(instance)
        return objects
