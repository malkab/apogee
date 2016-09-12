#!/usr/bin/env python
# coding=UTF8

import copy, yaml

### TODO: continue defining basic YAML processing,
### final YAML formats and capabilities for configuration, catalog, and scripts
### Implement DB object model and work out automatic generation from YAML info.

# Class Apogee

class Apogee(object):
    """
    This class holds methods basic high-level
    operative functions of Apogee.
    """

    def __init__(self):
        """
        Initializator.
        """
        self.catalog = None
        """YAML DB objects catalog."""
        
        self.configuration = None
        """Configurations YAML."""
        
        self.scripts = None
        """Scripts YAML."""
        
        self.objects = {}
        """Processed objects."""


    def cliError(self, error, forwardedException):
        """
        Displays a CLI error.
        """
        print "------------------------------"
        print "ERROR: %s" % error
        print
        print forwardedException
        print "------------------------------"                                        
        sys.exit(1)        

                
    def loadCatalog(self, catalogName="catalog.yml"):
        """
        Loads a catalog, a YAML file with object definitions.

        catalogName: Name of the catalog file, "catalog.yml" by default.
        """
        try:
            with open(catalogName, "r") as stream:
                try:
                    self.catalog = yaml.load(stream)
                except yaml.scanner.ScannerError as e:
                    self.cliError("Catalog %s YAML file malformed:" % catalogName, e)

        except IOError as e:
            self.cliError("Catalog file %s not found" % catalogName, e)


    def __dictSubstitution(self, dictionary, macros, startMark="_{", endMark="}_"):
        """
        Substitutes macros in a dictionary.

        dictionary: Dictionary to perform substitution on.
        macros: Macros dictionary.
        startMark: Star mark, defaults to "_{"
        endMark: End mark, defaults to "}_"
        """

        for k,v in dictionary.iteritems():
            if startMark in v:
                tag = v[v.find(startMark)+len(startMark):v.find(endMark)]
                dictionary[k] = macros[tag]

        return dictionary
        

    def expandCatalog(self, objects):
        """
        Deals with catalog 'with' expansion.

        TODO: Make private.
        """

        # Is objects a list?
        if isinstance(objects, list):
            # Iterator to walk trough the list as it potentially grows
            i = 0

            # Iterate...
            while i<len(objects):

                # Is the next element a dict?
                if isinstance(objects[i], dict):
                    # and has a loop clause?
                    if "with" in objects[i].keys():
                        # iterate the loop and generate parsed clones of itself
                        for w in objects[i]["with"]:
                            cobject = copy.deepcopy(objects[i])
                            # pop the loop from the clone
                            cobject.pop("with", None)
                            # append the parsed clone to the list
                            objects.append(self.__dictSubstitution(cobject, w))

                        # Once iterations are over, delete the original with element
                        objects.pop(i)
                    else:
                        # If there is no "with", just process the dictionary as normal and advance to the
                        # next element
                        objects[i] = self.expandCatalog(objects[i])
                        i += 1
                else:
                    # if its a list or scalar, just process as normal and advance
                    objects[i] = self.expandCatalog(objects[i])
                    i += 1
                        
        if isinstance(objects, dict):
            # If a dict, process as normal
            for k,v in objects.iteritems():
                objects[k] = self.expandCatalog(v)

        # Return if a scalar or done processing
        return objects
