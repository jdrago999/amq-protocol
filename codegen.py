#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re

sys.path.append(os.path.join("vendor", "rabbitmq-codegen"))

from amqp_codegen import *
try:
    from jinja2 import Template
except ImportError:
    print "Jinja2 isn't installed. Run easy_install Jinja2 or pip install Jinja2."
    sys.exit(1)

# main class
class AmqpSpecObject(AmqpSpec):
    IGNORED_CLASSES = ["access", "tx"]
    IGNORED_FIELDS = {
        'ticket': 0,
        'nowait': 0,
        'capabilities': '',
        'insist' : 0,
        'out_of_band': '',
        'known_hosts': '',
    }

    def __init__(self, path):
        AmqpSpec.__init__(self, path)

        for item in self.classes:
            item.banned = bool(item.name in self.__class__.IGNORED_CLASSES)

        self.classes = filter(lambda item: not item.banned, self.classes)

# I know, I'm a bad, bad boy, but come on guys,
# monkey-patching is just handy for this case.
# Oh hell, why Python doesn't have at least
# anonymous functions? This looks so ugly.
original_init = AmqpEntity.__init__
def new_init(self, arg):
    original_init(self, arg)
    constant_name = ""
    for chunk in self.name.split("-"):
        constant_name += chunk.capitalize()
    self.constant_name = constant_name
AmqpEntity.__init__ = new_init

# method.accepted_by("server")
# method.accepted_by("client", "server")
accepted_by_update = json.loads(file("amqp_0.9.1_changes.json").read())

def accepted_by(self, *receivers):
    def get_accepted_by(self):
        try:
            return accepted_by_update[self.klass.name][self.name]
        except KeyError:
            return ["server", "client"]

    def list_include(list, item):
        try:
            list.index(item)
            return True
        except ValueError:
            return None

    actual_receivers = get_accepted_by(self)
    return all(map(lambda receiver: list_include(actual_receivers, receiver), receivers))

AmqpMethod.accepted_by = accepted_by

# helpers
def render(path, **context):
    file = open(path)
    template = Template(file.read())
    return template.render(**context)

def main(json_spec_path):
    spec = AmqpSpecObject(json_spec_path)
    classes = spec.classes
    print render("protocol.rb.pytemplate", spec = spec, classes = classes)

if __name__ == "__main__":
    do_main_dict({"spec": main})