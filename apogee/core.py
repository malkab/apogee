#!/usr/bin/env python
# coding=UTF8


"""

Apogee core classes.

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


class Comment(object):
    """
    Comment class. All methods are static for easy to use.
    """

    
    @staticmethod
    def block(comment):
        """
        Creates a block comment.

        :param comment: Comment.
        :type comment: String
        :return: String
        """
        
        if isinstance(comment, dict):
            c = comment["comment"]
        else:
            c = comment
            
        return "/*\n\n  %s\n\n*/\n\n" % c

    
    @staticmethod
    def echoDash(comment):
        """
        Creates an echoDash comment.

        :param comment: Comment.
        :type comment: String
        :return: String
        """
        
        if isinstance(comment, dict):
            c = comment["comment"]
        else:
            c = comment
        
        l = len(c)
        dash = "-" * l
        return "\echo %s\n\echo %s\n\echo %s\n\n" % (dash, c, dash)

    
    @staticmethod
    def echo(comment):
        return "\echo %s\n\n" % comment

    
    @staticmethod
    def comment(comment):
        return "-- %s\n\n" % comment

    
    @staticmethod
    def blank(n=1):
        return "\n" * n



class Role(object):
    """
    Database role.
    """

    name = None
    """Role name."""

    group = False
    """Is the role a group?"""
    
    nologin = True
    """Login or not login?"""

    inherit = False
    """Inherit from another role."""

    inrole = None
    """Inheriting role."""

    password = None
    """Role password."""

    comment = None
    """Role comment."""

    def __init__(self, name, password=None, group=False, nologin=False, inherit=True, inrole=None, comment=None):
        """
        Creates a new role.

        :param name: Name of the role.
        :type name: String
        :param password: Role password. Defaults to None.
        :type password: String
        :param group: If the role is a group. Defaults to False.
        :type group: Boolean
        :param nologin: If the role has login privilege or not. Defautls to False.
        :type nologin: Boolean
        :param inherit: If the role inherits privileges. Defaults to True.
        :type inherit: Boolean
        :param inrole: Parent role. Defaults to None.
        :type inrole: apogee.core.Role
        :param comment: Role comment. Defaults to None.
        :type comment: String
        """
        
        self.name = name
        self.group = group
        self.nologin = nologin
        self.inherit = inherit
        self.inrole = inrole
        self.password = password
        self.comment = comment

    def drop(self):
        """
        Drops role.
        """
        return "drop role %s;\n\n" % self.name
        
    def fullCreate(self):
        """
        Full create script, comments and create.
        """
        return self.codeComment()+self.create()+self.sqlComment()
        
    def alterPassword(self, password=None):
        """
        Alters password.

        :param password: New password. Defaults to the current password.
        :type password: String.
        """
        password = self.password if password is None else password
        return "alter role %s password '%s';\n\n" % (self.name, password)

    def codeComment(self):
        """
        Code comment.
        """
        if self.comment:
            return Comment.comment(self.comment)
        else:
            return ""
    
    def sqlComment(self):
        """
        SQL comment.
        """
        if self.comment:
            return "comment on role %s is\n'%s';\n\n" % (self.name, self.comment)
        else:
            return ""
    
    def create(self):
        """
        Create script.
        """
        out = "create role %s with %s%s%s%s;\n\n" % (self.name, \
                                                       "nologin " if self.nologin else "login ", \
                                                       "inherit " if self.inherit else "", \
                                                       "in role %s " % self.inrole.name if self.inrole else "", \
                                                       "password '%s'" % self.password if self.password else "")
        return out

    def revoke(self, dbObject, privileges):
        """
        Revoke permissions on database object.

        :param dbObject: Database object to grant permissions on (currently Database or Schema).
        :type dbObject: apogee.core.Database or apogee.core.Schema
        :param privileges: List of privileges to grant on database object.
        :type privileges: List of strings
        """
        if str(dbObject.__class__)=="<class 'apogee.core.Database'>":
            objType = "database"
        elif str(dbObject.__class__)=="<class 'apogee.core.Schema'>":
            objType = "schema"

        privileges = privileges if isinstance(privileges, list) else [privileges]            
        priv = ', '.join(privileges)

        return "revoke %s on %s %s from %s;\n\n" % (priv, objType, dbObject.name, self.name)

    def grant(self, dbObject, privileges):
        """
        Grant permissions on database object.

        :param dbObject: Database object to grant permissions on (currently Database or Schema).
        :type dbObject: apogee.core.Database or apogee.core.Schema
        :param privileges: List of privileges to grant on database object.
        :type privileges: List of strings        
        """
        if str(dbObject.__class__)=="<class 'apogee.core.Database'>":
            objType = "database"
        elif str(dbObject.__class__)=="<class 'apogee.core.Schema'>":
            objType = "schema"

        privileges = privileges if isinstance(privileges, list) else [privileges]
        priv = ', '.join(privileges)

        return "grant %s on %s %s to %s%s;\n\n" % (priv, objType, dbObject.name, \
                                                    "group " if self.group else "", self.name)

    def grantOnAllTablesInSchema(self, dbObject, privileges):
        """
        Grant permissions on all tables of a schema.

        :param dbObject: Database object to grant permissions on (currently Database or Schema).
        :type dbObject: apogee.core.Database or apogee.core.Schema
        :param privileges: List of privileges to grant on database object.
        :type privileges: List of strings        
        """
        priv = ', '.join(privileges)

        return "grant %s on all tables in schema %s to %s%s;\n\n" % (priv, dbObject.name, \
                                                                     "group " if self.group else "", self.name)
                                                    




    
class Script(object):
    """
    Script class. This class generates script to files.
    """

    
    basePath = None
    """Base path to drop files in."""

    name = None
    """Name of file of the script to be created."""

    items = None
    """Items to be processed in the script."""

        
    def __init__(self, params):
        """
        Manage files and render scripts.

        :param params: Dictionary with params.
        :type params: Dict
        """

        if params:
            self.basePath = params["basePath"] if "basePath" in params.keys() else "."
            self.name = params["name"]
            self.items = params["items"]

        print "ii", self.basePath, self.name, self.items
    
    
    def render(self):
        """
        Renders a set of commands to a file. Commands are dicts describing Apogee objects.
        """
                
        try: 
            os.makedirs(self.basePath)
        except:
            pass
            
        f = open(path+"/"+self.name, "w")

        f.write(Comment.block("File: %s" % self.name))
        f.write(Comment.echoDash("Running script file: %s" % self.name))
        
        for c in self.items:
            f.write(c)

        f.write(Comment.echoDash("Run of script file ended: %s" % self.name))
        f.write(Comment.block("End of file: %s" % self.name))
            
        f.close()



class Role(object):
    def __init__(self, i):
        print "Role init"
        
    def alterPassword(self):
        print "alterPassword"
        
