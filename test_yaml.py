#!/usr/bin/env python
# coding=UTF8

import yaml, apogee.core as c

conf = {
    "role_geoserver": "caca",
    "a": "pedo"
    }

with open("dictionary.yml", "r") as stream:
    obj = yaml.load(stream)

objs = {
    "role": "_@role_geoserver",
    "je": "_@a",
    "list": ["_@a", "_@role_geoserver", ["_@a", "_@a"]],
    "dict": {
        "r": "_@a",
        "k": "_@a",
        "list": ["_@a", "_@role_geoserver", ["_@a", "_@a"]]
        }
    }

print c.Helpers.parseConf(objs, conf)
