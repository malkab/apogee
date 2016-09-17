#!/usr/bin/env python
# coding=UTF8



# -------------------
# Base DbObject class
# -------------------

class DbObject(object):
    """
    Base class for all db objects. All DB objects must inherit this class and
    reimplement its methods.
    """

    def __init__(self, id, apogee, name, comment=None):
        """
        Initializator.

        apogee: Parent apogee instance.
        name: Name of the object.
        comment: Comment of the object.
        """

        self.id = id
        self.apogee = apogee
        self.name = name
        self.comment = comment


    def drop(self):
        """
        Drop command. Must return a string.
        """
        
        raise NotImplementedError("drop not implemented.")


    def fullDrop(self):
        """
        Full drop command, with comments. Must return a string.
        """

        raise NotImplementedError("fullDrop not implemented.")
    

    def fullCreate(self):
        """
        Full create scripts, comments and create. Must return a string.
        
        """
        
        raise NotImplementedError("fullCreate not implemented.")


    def codeComment(self):
        """
        Code comment. Must return a string.
        """
        
        if self.comment:
            return Global.comment(self.comment)
        else:
            return ""


    def sqlComment(self):
        """
        SQL comment. Must return a string.
        """
        
        raise NotImplementedError("sqlComment not implemented.")


    def create(self):
        """
        Create script. Must return a string.
        """
        
        raise NotImplementedError("create not implemented.")


    def mkdocs(self):
        """
        Create MkDocs string. Must return a string.
        """
        
        raise NotImplementedError("mkdocs not implemented.")










class Group(DbObject):
    """
    Database role.

    TODO: Redefine Group object both in the YAML as in the Python.
    """
    
    def __init__(self, apogee, name, id, expandable, comment):
        """
        Creates a new role.
        """

        self.expandable = expandable

        DbObject.__init__(self, id, apogee, name, comment)
    



class Role(DbObject):
    def __init__(self, apogee, name, id, comment):
        """
        Creates a new role.
        """

        DbObject.__init__(self, id, apogee, name, comment)



class Database(DbObject):
    def __init__(self, apogee, name, id, comment, schemas):
        """
        Creates a new role.
        """

        self.schemas = schemas
        
        DbObject.__init__(self, id, apogee, name, comment)
