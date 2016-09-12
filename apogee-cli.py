#!/usr/bin/env python
# coding=UTF8

import apogee.core as core
reload(core)

a = core.Apogee()

a.loadCatalog()

a.expandCatalog(a.catalog)

# a.cleanWith(a.catalog)

print
print "Final: ", a.catalog
print



# a.processTarget()

