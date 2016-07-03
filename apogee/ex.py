#!/usr/bin/env python
# coding=UTF8


"""

Apogee executable classes.

This file is part of Apogee.

Apogee is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Apogee is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Apogee.  If not, see <http://www.gnu.org/licenses/>.

"""


import importlib, os, sys, core, __builtin__, collections

class Executable(object):
    """
    This class encapsulates the methods required by the Apogee executable.
    """

    module = None
    """Pointer to the imported module."""

    config = None
    """Pointer to the imported config module."""
    
    
    def __init__(self, moduleName, configName, config):
        """
        Class for the Apogee executable.

        :param moduleName: Name of the module to import with Apogee definitions.
        :type moduleName: String
        :param configName: Name of the config module.
        :type configName: String
        :param config: Name of the config setup to be used.
        :type config: String
        """

        sys.path.append(os.path.dirname(os.path.realpath(__file__))+'/..')

        # Add config module to globals so the script module knows the config
        self.config = importlib.import_module(configName.rstrip(".py"))
        c = getattr(self.config, config)
        __builtin__.config = c

        # Import script module
        self.module = importlib.import_module(moduleName.rstrip(".py"))

                
    def getApogeeDefs(self):
        """
        Get a list with Apogee definitions found in module.

        :return: List of strings.
        """

        out = collections.OrderedDict()

        for i in dir(self.module):
            o = getattr(self.module, i)

            if isinstance(o, dict):
                if i != "__builtins__":
                    out[i] = o

        return out


    def execute(self):
        """
        Executes all ap_ items in the imported module.
        """

        for k,v in self.getApogeeDefs().iteritems():
            # o = getattr(self.module, i)

            # print k,v

            if "class" in v.keys():
                if v["class"] == core.Script:
                    print v

                    for i in v["items"]:
                        print i

                        if "object" in i.keys():
                            obj = i["object"]["class"](i)
                            print obj
                            obj[
                        else:
                            print i["method"](i)
            
