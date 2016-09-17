#!/usr/bin/env python
# coding=UTF8

import apogee.core as core, pprint
reload(core)

a = core.Apogee()

a.processCatalog(catalog="Tests/catalog_nested_loops.yml")

print
pprint.pprint(a.catalog)
print




