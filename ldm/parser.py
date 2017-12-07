import re, json

class Node(object):
    def __init__(self, name):
        self.name = name
        self.props = {}
        self.childs = []

    def add_child(self, node):
        node.parent = self
        self.childs += [node]

    def get_child(self, name):
        for ch in self.childs:
            if ch.name == name:
                return ch
        return None

    def dump_childs(self):
        ret = {
            "name": self.name,
            "props": self.props,
            "childs": []
        }
        for child in self.childs:
            ret["childs"] += [child.dump_childs()]
        return ret

    def __getitem__(self, name):
        return self.props[name]

    def __setitem__(self, name, val):
        self.props[name] = val

class Matcher(object):
    def __init__(self, ldm, pattern):
        self.curr_line = 0
        self.results = []
        self.lines = pattern.split("\n")

    def __call__(self, line):
        if len(self.lines) == 1:
            ret = re.match(self.lines[0], line)
            if ret:
                return list(ret.groups())
            return None
        else:
            ret = re.match(self.lines[self.curr_line], line)
            if ret:
                self.results += ret.groups()
                self.curr_line += 1
            else:
                self.results = []
                self.curr_line = 0
            if self.curr_line >= len(self.lines):
                self.curr_line = 0
                ret = self.results
                self.results = []
                return ret
            return None


class Parser(object):
    def __init__(self):
        self.rules = {}
        self.root_node = Node("")
        self.curr_node = self.root_node

    def add_rule(self, file, pattern, handler):
        file = file or ".*"
        if self.rules.get(file) is None:
            self.rules[file] = {}
        self.rules[file][pattern] = handler

    def parse(self, filename, io):
        parsers = []
        for file_mask in self.rules:
            if re.match(file_mask, filename):
                pair = self.rules[file_mask]
                for pattern in pair:
                    parsers += [{
                        'matcher': Matcher(self, pattern),
                        'handler': pair[pattern]
                    }]

        for line in io:
            for parser in parsers:
                ret = parser['matcher'](line)
                if ret:
                    parser['handler'](self, *ret)

    def parse_file(self, file):
        with open(file) as f:
            self.parse(file, f.readlines())

    def add_node(self, node_path):
        node = Node(node_path)
        self.curr_node.add_child(node)
        return node

    def find(self, node_path):
        assert type(node_path) == type("")

        is_abs = node_path.startswith("/")
        nodes = node_path.split("/")
        node = self.root if is_abs else self.curr_node
        for n in reversed(nodes):
            if n == ".":
                pass
            elif n == "..":
                node = node.parent
            else:
                node = node.get_child(n)
            if node is None:
                raise "Node was not found: " + node_path

    def move_to(self, node_path):
        if type(node_path) is Node:
            self.curr_node = node_path
        else:
            self.curr_node = find(node_path)

    def get_raw_data(self):
        return self.root_node.dump_childs()

    def rule(self, *argv):
        assert len(argv) >= 1
        pattern = argv[1] if len(argv) == 2 else argv[0]
        file = argv[0] if len(argv) == 2 else None
        def rule_adder(func):
            self.add_rule(file, pattern, func)
        return rule_adder
