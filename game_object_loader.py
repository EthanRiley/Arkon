import json, re, copy

class object_loader:

    def get_classes(self, filename):
        file = open(filename).read()
        regex = re.compile("class\s(\w+)")
        classes = regex.findall(file)
        return classes


    def __init__(self, filename):
      self.json = json.loads(open(filename).read())
      self.objects = self.get_classes("game_objects.py")

    def __get_types(self):
        types = {}
        for Type in self.json["types"]:
            name = Type.name
            Type.pop("name")
            complete_type = self.json["default"].copy()
            complete_type.update(Type)
            types[name] = complete_type

        self.json.pop("types")
        return types

    def load(self):
        types = self.__get_types()
        objects = []
        for Type in self.json:
            for instance in self.json[Type]:
                instance.update(types[Type])
                objects.append(instance)
        return objects
