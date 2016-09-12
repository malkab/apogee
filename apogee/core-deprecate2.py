#!/usr/bin/env python
# coding=UTF8

# import os, distutils.dir_util, sys, yaml, copy
import yaml, copy, os, dbobjects, shutil, sys, inspect
reload(dbobjects)
# from subprocess import call


# # Class Apogee

# class Apogee(object):
#     """
#     This class holds methods basic high-level
#     operative functions of Apogee.
#     """

#     catalogDict = None 
#     """
#     List of objects. Items are dictionaries with the following items:

#     {"name": Name of the object, "object": The object itself}
#     """

#     configuration = None
#     """Configuration."""

#     catalog = None
#     """Original object catalog."""


#     def __init__(self):
#         """
#         Initializator.
#         """
#         self.catalogDict = {}

                
    def loadCatalog(self, catalogName="catalog.yml", configuration="apogeeconf.yml"):
        """
        Loads a catalog, a YAML file with object definitions.
        Loads also the configuration.
        """
        try:
            with open(configuration, "r") as stream:
                obj = yaml.load(stream)

            self.configuration = obj
        except:
            pass
        
        with open(catalogName, "r") as stream:
            try:
                self.catalog = yaml.load(stream)
            except yaml.scanner.ScannerError as e:
                print "------------------------------"
                print "ERROR: Catalog YAML malformed:"
                print
                print e
                print "------------------------------"                                
                sys.exit(1)

            
    def parse(self, objects, configuration, mark="_@"):
        """
        Gets a dictionary or list of objects and search for macro expansion
        mark in values. When found, it performs the substitution.
        """

        if isinstance(objects, list):
            for i in range(0, len(objects)):
                objects[i] = self.parse(objects[i], configuration, mark)
        
        if isinstance(objects, dict):
            for k,v in objects.iteritems():
                objects[k] = self.parse(v, configuration, mark)

        if isinstance(objects, (str, unicode)):
            for k,v in configuration.iteritems():
                if v:
                    objects = objects.replace("%s%s%s" % (mark, k, mark), unicode(v))
                
        return objects


    def processTarget(self, target=None):
        """
        Process a target.
        """
        # Drop build folder
        try:
            shutil.rmtree("build")
        except:
            pass
        
        for k,v in self.configuration["targets"].iteritems():
            # Reset catalog
            self.catalogList = []
            
            print "Processing target %s..." % k
            
            # Dictionaries fusion to get a whole 
            config = copy.deepcopy(self.configuration["globals"])
            config.update(v)
            
            # Parse
            objs = copy.deepcopy(self.catalog)

            for obj in objs:
                # Check for absence of id
                if "id" not in obj.keys():
                    print "-------------------------------"
                    print "Error: Object %s lacks id" % obj["name"]
                    print "-------------------------------"
                    print "Offending object is:"
                    print obj
                    sys.exit(1)

                type = obj["id"][0:obj["id"].find("::")]
                    
                dbo = [i[0] for i in inspect.getmembers(dbobjects, inspect.isclass)]
                    
                if type not in dbo:
                    print "-------------------------------"
                    print "Error: Unknown %s type in object %s" % (type, obj["name"])
                    print "-------------------------------"
                    print "Offending object is:"
                    print obj
                    sys.exit(1)                    

                finalObjects = []
                        
                # Check if there is a with, iterate, and create new items
                if "with" in obj.keys():
                    for withIteration in obj["with"]:
                        toParse = copy.deepcopy(obj)
                        toParse.pop("with", None)
                        self.parse(toParse, withIteration, "_#")
                        finalObjects.append(toParse)

                finalObjects = [obj] if finalObjects==[] else finalObjects

                for finalObject in finalObjects:
                    self.parse(finalObject, config)
                    args = copy.deepcopy(finalObject)
                    args["apogee"] = self
                    args.pop("with", None)
                    id = args.pop("id", None)
                    self.catalogDict[id] = getattr(dbobjects, type)(**args)

            # Open target folder
            os.makedirs("build/%s" % k)

            # Get Scripts             
            for script in self.getTypeFromCatalog(dbobjects.Script):
                print "Writting script %s..." % script.name
                script.write("build/%s" % k)

                                    
    def getFromCatalog(self, id):
        """
        Returns an object from the catalogs with descriptor and from a given class.
        Two possible arguments:

        id: A string with the object ID to retrieve.
        """

        if id not in self.catalogDict.keys():
            raise ApogeeException("Object %s not found in catalog." % id)

        return self.catalogDict[id]


    def getTypeFromCatalog(self, type, remove=None):
        """
        Returns an object type from the catalog.

        type: A class or list of classes from dbobjects.
        remove: Optionally a list or string with the name of elements to be removed from the selection.
        """
        remove = remove if isinstance(remove, list) else [remove]
        select = copy.deepcopy(self.catalogDict)

        # Selection
        select = {k: v for k,v in select.iteritems() if isinstance(v, type)}
        
        # Removal from selection, if applicable
        select = [i for k,i in select.iteritems() if k not in remove] if remove else select

        return select





# ----------------
# Apogee exception
# ----------------

class ApogeeException(Exception):
    """
    Apogee exception.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "Apogee exception: %s" % self.value
        
