#!/usr/bin/env python
# coding=UTF8

import copy, yaml, sys, apogee.dbobjects as dbobjects

reload(dbobjects)

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


    # TODO: Rewrite, this functionality has gone to yates
    def __loadCatalog(self, catalog):
        """
        Loads a catalog, a YAML file with object definitions.

        catalog: Name of the catalog file, "catalog.yml" by default.
        """
        try:
            with open(catalog, "r") as stream:
                try:
                    self.catalog = yaml.load(stream)
                except yaml.scanner.ScannerError as e:
                    self.cliError("Catalog %s YAML file malformed:" % catalog, e)

        except IOError as e:
            self.cliError("Catalog file %s not found" % catalog, e)


    def __dictSubstitution(self, dictionary, macros, startMark="_{", endMark="}_"):
        """
        Substitutes macros in a dictionary.

        dictionary: Dictionary to perform substitution on.
        macros: Macros dictionary.
        startMark: Star mark, defaults to "_{"
        endMark: End mark, defaults to "}_"
        """

        for k,v in dictionary.iteritems():
            if isinstance(v, (str, unicode)) and startMark in v:
                start = v.find(startMark)
                end = v.find(endMark)
                tag = v[start+len(startMark):end]
                dictionary[k] = v[:start]+macros[tag]+v[end+len(endMark):]

        return dictionary
        

    def __expandWithCatalog(self, objects):
        """
        Deals with catalog 'with' expansion.
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
                        # If there is no "with" nor "expandList",
                        # just process the dictionary as normal
                        # and advance to the next element
                        objects[i] = self.__expandWithCatalog(objects[i])
                        i += 1
                else:
                    # if its a list or scalar, just process as normal and advance
                    objects[i] = self.__expandWithCatalog(objects[i])
                    i += 1
                        
        if isinstance(objects, dict):
            # If a dict, process as normal
            for k,v in objects.iteritems():
                objects[k] = self.__expandWithCatalog(v)

        # Return if a scalar or done processing
        return objects


    def processCatalog(self, catalog="catalog.yml"):
        self.__loadCatalog(catalog)
        self.__expandWithCatalog(self.catalog)

        processingPrecedence = ["Group", "Role", "Database"] #, "Column",
                                # "Table", "View", "Schema", "Script"]

        # Iterate types of objects and try to convert them to proper objects
        for i in processingPrecedence:
            for c in self.catalog:
                if c["id"][:c["id"].find("::")]==i:
                    type = c["id"][0:c["id"].find("::")]
                    c["apogee"] = self
                    self.objects[c["id"]] = getattr(dbobjects, type)(**c)
                    
                
        # self.__expandListCatalog(self.catalog)

