import json
from ldm import Parser

parser = Parser()

parser.parse_file()

def raw_print(node, indent = 0):
    if node["name"] != "":
        preff = " " * indent
        print(preff + "--")
        print(preff + node["name"])
        for prop in node["props"]:
            print(preff + prop + ": " + node["props"][prop])
    for ch in node["childs"]:
        raw_print(ch, indent + 4 if node["name"] != "" else 0)

raw_print(parser.get_raw_data())
# print(json.dumps(parser.get_raw_data(), indent=4))
