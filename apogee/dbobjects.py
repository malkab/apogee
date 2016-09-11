#!/usr/bin/env python
# coding=UTF8

#import os, distutils.dir_util, sys, yaml, copy
import codecs, os, copy, sys
#from subprocess import call


# -------------------
# Base DbObject class
# -------------------

class DbObject(object):
    """
    Base class for all db objects. All DB objects must inherit this class and
    reimplement its methods.
    """

    def __init__(self, apogee, name, comment=None):
        """
        Initializator.

        apogee: Parent apogee instance.
        name: Name of the object.
        comment: Comment of the object.
        """

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
    




# -------------
# Global object
# -------------

class Global(object):
    """
    Global class.

    This class holds a bunch of static methods that doesn't belong
    to any other place.
    """
    
    @staticmethod
    def block(comment):
        return "/*\n\n  %s\n\n*/\n\n" % comment

    
    @staticmethod
    def echoDash(comment):
        dash = "-" * len(comment)
        return "\echo %s\n\echo %s\n\echo %s\n\n" % (dash, comment, dash)

    
    @staticmethod
    def echo(comment):
        return "\echo %s\n\n" % comment

    
    @staticmethod
    def comment(comment):
        return "-- %s\n\n" % comment

    @staticmethod
    def commit():
        return "commit;\n\n"

    @staticmethod
    def begin():
        return "begin;\n\n"




                
# ----------
# Role class
# ----------

class Role(DbObject):
    """
    Database role.

    TODO: Redefine Group object both in the YAML as in the Python.
    """
    
    def __init__(self, apogee, name, password=None,
                 nologin=False, inherit=True,
                 ingroup=None, comment=None):
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
        
        self.nologin = nologin
        self.inherit = inherit
        self.ingroup = ingroup
        self.password = password

        DbObject.__init__(self, apogee, name, comment)

        
    def drop(self):
        """
        Drops role.
        """
        
        return "drop role %s;\n\n" % self.name


    def fullDrop(self):
        """
        Full drop for the role.
        """
        return \
            Global.comment("Dropping role %s" % self.name)+ \
            Global.echo("Dropping role %s" % self.name)+ \
            self.drop()

            
    def fullCreate(self):
        """
        Full create script, comments and create.
        """
        
        return self.codeComment()+ \
          Global.echo("Creating role %s" % self.name) + \
          self.create()+ \
          self.sqlComment()+"\n"

            
    def alterPassword(self, password=None):
        """
        Alters password.

        :param password: New password. Defaults to the current password.
        :type password: String.
        """
        
        password = self.password if password is None else password
        return "alter role %s password '%s';\n\n" % (self.name, password)

            
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
        
        out = "create role %s with %s%s%s%s;\n\n" % \
          (self.name, "nologin " if self.nologin else "login ", \
           "inherit " if self.inherit else "", \
           "in role %s " % self.apogee.getFromCatalog(self.ingroup).name if self.ingroup else "", \
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

        if str(dbObject.__class__)=="<class 'apogee.dbobjects.Database'>":
            objType = "database"
        elif str(dbObject.__class__)=="<class 'apogee.dbobjects.Schema'>":
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

        if str(dbObject.__class__)=="<class 'apogee.dbobjects.Database'>":
            objType = "database"
        elif str(dbObject.__class__)=="<class 'apogee.dbobjects.Schema'>":
            objType = "schema"

        privileges = privileges if isinstance(privileges, list) else [privileges]
        out = ""
        
        if "select all tables" in privileges:
            out += "grant select on all tables in %s %s to %s;\n\n" % (objType, dbObject.name, self.name)
            privileges.remove("select all tables")

        if privileges!=[]:
            priv = ', '.join(privileges)
            out += "grant %s on %s %s to %s;\n\n" % (priv, objType, dbObject.name, self.name)

        return out

                                                    
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

                                                                     
    def mkdocs(self):
        """Returns the MkDocs string."""
        
        return \
          "__Role %s (in group %s, with %s, %s, in role %s):__ %s" % \
          (self.name, self.group, self.nologin, self.inherit, \
           self.inrole, self.comment)





# -----------
# Group class           
# -----------

class Group(DbObject):
    """
    Group role, just a distinctive name for certain roles.
    The reason this class exists is to create group roles before roles
    assigned to them.
    """

    def __init__(self, apogee, name, inherit=True, ingroup=None,
                 comment=None):

        self.ingroup = ingroup
        self.inherit = inherit
        
        DbObject.__init__(self, apogee, name, comment)


    def drop(self):
        """
        Drops group.
        """
        
        return "drop role %s;\n\n" % self.name


    def fullDrop(self):
        """
        Full drop for the group.
        """
        return \
            Global.comment("Dropping group %s" % self.name)+ \
            Global.echo("Dropping group %s" % self.name)+ \
            self.drop()

         
    def sqlComment(self):
        """
        SQL comment.
        """
        
        if self.comment:
            return "comment on role %s is\n'%s';\n\n" % (self.name, self.comment)
        else:
            return ""
        
        
    def fullCreate(self):
        """
        Full create script, comments and create.
        """
        
        return self.codeComment()+ \
          Global.echo("Creating group %s" % self.name)+ \
          self.create()+ \
          self.sqlComment()+"\n"


    def create(self):
        """
        Create script.
        """
        
        out = "create role %s with nologin %s%s" % \
           (self.name,
            "inherit " if self.inherit else "", \
            "in role %s " % self.apogee.getFromCatalog(self.ingroup).name if self.ingroup else "")
           
        return out.strip()+";\n\n"

    
    def revoke(self, dbObject, privileges):
        """
        Revoke permissions on database object.

        :param dbObject: Database object to grant permissions on (currently Database or Schema).
        :type dbObject: apogee.core.Database or apogee.core.Schema
        :param privileges: List of privileges to grant on database object.
        :type privileges: List of strings
        """

        if str(dbObject.__class__)=="<class 'apogee.dbobjects.Database'>":
            objType = "database"
        elif str(dbObject.__class__)=="<class 'apogee.dbobjects.Schema'>":
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
        
        if str(dbObject.__class__)=="<class 'apogee.dbobjects.Database'>":
            objType = "database"
        elif str(dbObject.__class__)=="<class 'apogee.dbobjects.Schema'>":
            objType = "schema"

        privileges = privileges if isinstance(privileges, list) else [privileges]
        out = ""
        
        if "select all tables" in privileges:
            out += "grant select on all tables in %s %s to group %s;\n\n" % (objType, dbObject.name, self.name)
            privileges.remove("select all tables")

        if privileges!=[]:
            priv = ', '.join(privileges)
            out += "grant %s on %s %s to group %s;\n\n" % (priv, objType, dbObject.name, self.name)

        return out
                
                


    
# ------------
# Script class
# ------------

class Script(object):
    """
    Script class.
    """        
    
    def __init__(self, apogee, name=None, file=None, comment=None, content=None):
        """
        Script class.
        """
        
        self.apogee = apogee
        """Parent Apogee."""
        
        self.name = name
        """Script name."""

        self.file = file
        """File name, path included, if any."""
        
        self.comment = comment
        """Script comment."""

        self.content = content
        """Script content."""
        
                
    def write(self, base):
        """
        Writes the script.

        base: base folder.
        """
        
        # Path analysis
        dirs = os.path.dirname(self.file)
        fileName = os.path.basename(self.file)

        try: 
            os.makedirs(base+"/"+dirs)
        except:
            pass
            
        f = codecs.open(base+"/"+self.file, encoding='utf-8', mode='w')        
        f.write(Global.block("File: %s" % self.file))
        f.write(Global.echoDash("Running script file: %s" % self.file))
        
        for c in self.content:
            # Single object action
            if "object" in c.keys():
                a = self.apogee.getFromCatalog((c["object"]))

                print "iuiu", a
                
                # Delete object and action keys to get args
                args = copy.deepcopy(c)
                args.pop("object", None)
                args.pop("action", None)
                f.write(getattr(a, c["action"])(**args))

            # family action
            if "family" in c.keys():
                if "but" in c.keys():
                    print c["family"]
                    l = self.apogee.getTypeFromCatalog(getattr(sys.modules[__name__], c["family"]), remove=c["but"])
                else:
                    l = self.apogee.getTypeFromCatalog(getattr(sys.modules[__name__], c["family"]))
                    
                for o in l:
                    f.write(getattr(o, c["action"])())

        f.write(Global.echoDash("Run of script file ended: %s" % self.file))
        f.write(Global.block("End of file: %s" % self.file))
            
        f.close()

        
    # def statics(self, folder="statics", path=None):
    #     """
    #     Copy all static files to the generation folder.

    #     :param folder: Folder where the static files are in. Defaults to 'statics'. If not, it is relative to the src folder.
    #     :type folder: String
    #     :param path: Path to drop files into. Optional. If this nor the class basePath is set defaults to the current folder. If set, it is relative to the basePath.
    #     :type path: String
    #     """
        
    #     path = self.basePath+"/"+path if path else (self.basePath if self.basePath else ".")
        
    #     distutils.dir_util.copy_tree(folder, path)
           

# --------------
# Class Database
# --------------

class Database(DbObject):
    """
    Database.
    """
        
    def __init__(self, apogee, name, host="localhost", port="5432", comment=None,
                 owner=None, permissions=None, extensions=None, tablespace=None):
        """
        Constructor.

        :param name: The name of the database.
        :type name: String
        :param name: Database host. Optional, defaults to localhost.
        :type name: String
        :param port: Database port. Optional, defaults to 5432.
        :type port: Integer or String
        :param comment: Database comment. Optional.
        :type comment: String
        :param owner: Database owner. Optional.
        :type owner: apogee.core.Role
        :param permissions: A tuple or list of tuples containing grants or revokes methods and a list of permissions. For example (role_whatever.grant, ["connect", "usage"). Optional.
        :type permissions: Tuple or list of tuples
        :param extensions: A apogee.core.Extension or list of such to create extensions into the database. Optional.
        :type extensions: apogee.core.Extension or list of apogee.core.Extension
        :param tablespace: The default database tablespace.
        :type tablespace: apogee.core.Tablespace
        """

        self.apogee = apogee
        self.name = name
        self.host = host
        self.port = str(port)
        self.comment = comment
        self.owner = owner if owner else None
        self.permissions = permissions if isinstance(permissions, list) else \
            ([permissions] if permissions is not None else None)
        self.extensions = extensions if isinstance(extensions, list) else [extensions]
        self.tablespace=tablespace

        DbObject.__init__(self, apogee, name, comment)
        
            
    def connect(self):
        """
        Outputs a \c command to the database.
        """

        return "\c %s\n\n" % (self.name)

    
    def create(self, owner=None):
        """
        Outputs database create string.

        :param owner: Owner of database. Optional. Defaults to the database owner, if any.
        :type owner: apogee.core.role
        """

        owner = owner if owner else (self.owner if self.owner else None)
        s = "create database %s%s%s" % \
          (self.name,
           " owner %s " % self.apogee.getFromCatalog(self.owner).name if self.owner else "",
           " tablespace %s" % self.tablespace.name if self.tablespace else "")

        return s.strip()+";\n\n"

    
    def codeComment(self):
        """
        Returns the code comment for the database.
        """
        return Global.comment(self.comment) if self.comment else ""


    def sqlComment(self):
        """
        Returns SQL comment statement for Database.
        """
        return "comment on database %s is\n'%s';\n\n" % (self.name, self.comment) if self.comment else ""
    

    def createPermissions(self):
        """
        Returns permissions creation for the database.
        """
        out = ""
        
        if self.permissions is not None:
            for i in self.permissions:
                rol = self.apogee.getFromCatalog(i["role"])
                x = getattr(rol, i["action"])
                out = out+x(self, i["privileges"])
            
        return out
    
    
    def fullCreate(self, owner=None):
        """
        Full create output for database. Outputs a code comment, the create, a SQL comment, grants and revokes, and extensions.

        :param superuser: An optional superuser with privileges to create extensions, if any.
        :type superuser: apogee.core.role
        :param owner: An optional owner. Defaults to the database owner.
        :type owner: apogee.core.role
        """
        
        owner = owner if owner else (self.owner if self.owner else None)
        
        out = \
            self.codeComment()+ \
            Global.echo("Creating database %s " % self.name) + \
            self.create(owner)+ \
            self.sqlComment()+ \
            self.createPermissions()+ \
            self.connect()+ \
            self.createExtensions()

        return out

              
    def createExtensions(self):
        """
        Creates extensions for the database.
        """

        out = ""
        
        for i in self.extensions:
            ext = self.apogee.getFromCatalog(i)
            out += "%s\n" % ext.create()
                
        return out
        
        
    def fullDrop(self):
        """
        Full drop for the database.
        """
        return \
            Global.comment("Dropping database %s" % self.name)+ \
            Global.echo("Dropping database %s" % self.name)+ \
            self.drop()


    def drop(self):
        """
        Drop for the database.
        """
        return "drop database %s;\n\n" % self.name


    def mkdocs(self):
        s = \
          "__Database %s at (%s, %s):__\n\n" % (self.name, self.host, self.port) + \
          "- owner: %s\n" % str(self.owner) + \
          "- permissions: %s\n" % str(self.permissions) + \
          "- extensions: %s\n" % str(self.extensions) + \
          "- tablespace: %s\n" % str(self.tablespace)
          
        return s





# ---------------
# Class Extension
# ---------------

class Extension(DbObject):
    """
    Database extension.
    """
    
    def __init__(self, apogee, name, comment):
        """
        Constructor.

        apogee: parent Apogee instance.
        name: extension name.
        comment: extension comment.
        """
        
        self.name = name
        self.comment = comment

        DbObject.__init__(self, apogee, name, comment)

        
    def create(self):
        """
        Returns the creation string for the extension.
        """
        return "create extension %s;\n" % self.name


    def mkdocs(self):
        return "__Extension %s:__ %s" % (self.name, self.comment)





# ------------
# Class Schema
# ------------

class Schema(DbObject):
    """
    Schema.
    """
        
    def __init__(self, apogee, name, comment, permissions=None, owner=None, tables=None, views=None):
        """
        Schema class.

        :param name: Name of the schema.
        :type name: String
        :param comment: Schema comment.
        :type comment: String
        :param permissions: A tuple or list of tuples containing grants or revokes. For example (role_whatever.grant, ["connect", "usage").
        :type permissions: Tuple or list of tuples
        :param owner: Owner role.
        :type owner: apogee.core.role
        :param tables: Tables belonging to the schema.
        :type tables: apogee.core.table or list of those.
        :param views: Views belonging to the schema.
        :type views: apogee.core.view or list of those.
        """
        
        self.name = name
        self.comment = comment
        self.permissions = permissions if isinstance(permissions, list) else [permissions]
        self.owner = owner
        self.tables = tables if isinstance(tables, list) else [tables]
        self.views = views if isinstance(views, list) else [views]

        DbObject.__init__(self, apogee, name, comment)

        
    def drop(self, cascade=False):
        return "drop schema %s%s;\n\n" % (self.name, " cascade" if cascade else "")


    def alterTableOwner(self, newowner, tables=None):
        """
        Changes ownership of tables in schema.

        newowner: New owner of tables.
        tables: Optional, a string or a list of strings of name tables to change ownership to.
        """
        tables = [tables] if isinstance(tables, str) else (tables if tables else self.tables)
        out = "".join([self.apogee.getFromCatalog(table).alterOwner(self, newowner) for table in tables])
        return out
        

    def alterViewOwner(self, newowner, views=None):
        """
        Changes ownership of views in schema.

        newowner: New owner of views.
        views: Optional, a string or a list of strings of name views to change ownership to.
        """
        views = [views] if isinstance(views, str) else (views if views else self.views)
        out = "".join([self.apogee.getFromCatalog(view).alterOwner(self, newowner) for view in views])
        return out

    
    def codeComment(self):
        return Global.comment(self.comment)

        
    def sqlComment(self):
        return "comment on schema %s is\n'%s';\n\n" % (self.name, self.comment)

    
    def fullRefresh(self):
        """
        Refreshes all materialized views in the schema.
        """
        
        out = Global.block("Refresh materialized view for schema %s" % self.name)+ \
            Global.echoDash("Starting: Refreshing materialized views for schema %s" % self.name)

        for i in self.views:
            if i.materialized:
                out += Global.echo("Materializing view %s" % i.name)+ \
                  i.refresh(self)+ \
                  i.vacuum(self)

        out += Global.echoDash("End: Refreshing materializing views for schema %s" % self.name)

        return out

    
    def create(self, owner=None):
        au = self.apogee.getFromCatalog(owner) if owner else self.apogee.getFromCatalog(self.owner)
        
        return "create schema %s%s;\n\n" % (self.name, \
                                            " authorization %s" % au.name if au else "")

                                            
    def alterOwner(self, newowner):
        newowner = self.apogee.getFromCatalog(newowner)
        return "alter schema %s owner to %s;\n\n" % (self.name, newowner.name)

    
    def setPermissions(self):
        out = ""
        
        if self.permissions is not None:
            for i in self.permissions:
                x = getattr(self.apogee.getFromCatalog(i["role"]), i["action"])
                out = out+x(self, i["privileges"])
            
        return out


    def fullCreate(self, blockComment=None, echoComment=None):
        """
        Full render of the schema.

        blockComment: a string with the block comment.
        echoComment: a string with the echo comment. Starting: and End: will be prefixed. If None, equals blockComment if present.
        """

        echoComment = echoComment if echoComment else (blockComment if blockComment else "")
        
        out = \
          (Global.block(blockComment) if blockComment else "") + \
          (Global.echoDash("Beginning: "+echoComment) if echoComment else "")+ \
          (Global.begin())+ \
          (self.codeComment())+ \
          (self.create())+ \
          (self.sqlComment())+ \
          (self.setPermissions())+ \
          ("".join([tables[i].fullCreate(self) for i in self.tables if i]))+ \
          ("".join([i.fullCreate(self) for i in self.views if i]))+ \
          (Global.commit())+ \
          (Global.echoDash("Ending: "+echoComment) if echoComment else "")

        return out


    def fullComment(self):
        """
        Full comment render of the schema.
        """
        
        out = \
            self.codeComment() + \
            self.sqlComment()

        for tableName in self.tables:
            table = self.apogee.getFromCatalog(tableName)
            out += table.sqlComment(self)
        
        return out
    
    
    def fullDrop(self, blockComment=None, echoComment=None):
        """
        Full drop of a schema.

        blockComment: a string with the block comment.
        echoComment: a string with the echo comment. Starting: and End: will be prefixed. Equals the blockComment if ommited.
        """

        echoComment = echoComment if echoComment else (blockComment if blockComment else "")
        
        return \
            (Global.block(blockComment) if blockComment else "")+ \
            (Global.echoDash("Beginning: "+echoComment) if echoComment else "")+ \
            (Helpers.begin())+ \
            (self.codeComment())+ \
            (self.drop(cascade=True))+ \
            (Helpers.commit())+ \
            (Global.echoDash("Ending: "+echoComment) if echoComment else "")


    def __str__(self):
        return "Database schema %s" % self.name
    

    def mkdocs(self):
        s = \
          "# __Schema %s__\n\n" % self.name + \
          "%s\n\n" % self.comment + \
          "- permissions: %s\n" % str(self.permissions) + \
          "- owner: %s\n\n" % str(self.owner)

        for t in self.tables:
            if t is not None:
                s += t.mkdocs()

        for v in self.views:
            if v is not None:
                s += v.mkdocs()

        return s+"\n"





# -----------
# Table class
# -----------

class Table(DbObject):
    """
    Table.
    """
        
    def __init__(self, apogee, name, comment, columns=None, keys=None, indexes=None, owner=None):
        self.name = name
        self.comment = comment

        # Process columns, must end in a list
        if columns is not None:
            columns = columns if isinstance(columns, list) else [columns]
            self.columns = [Column(**i) for i in columns]

        # Process keys, in the end it must be a list of column instances
        if keys is not None:
            self.keys = self.getColumns(keys)

        # Process index definitions
        if indexes is not None:
            self.indexes = indexes if isinstance(indexes, list) else [indexes]
            
            if self.indexes<>[]: 
                for i in range(0, len(self.indexes)):
                    self.indexes[i] = Index(iType=self.indexes[i]["type"],
                                            columns=self.getColumns(self.indexes[i]["columns"]),
                                            name=self.indexes[i]["name"])

        self.owner = owner
        
        DbObject.__init__(self, apogee, name, comment)
        

    def alterOwner(self, schema, newowner=None):
        newowner = newowner if newowner else self.owner
        newowner = self.apogee.getFromCatalog(newowner)
        schema = self.apogee.getFromCatalog(schema) if isinstance(schema, str) else schema
        return "alter table %s.%s owner to %s;\n\n" % (schema.name, self.name, newowner.name)

        
    def codeComment(self):
        return Global.comment(self.comment)

        
    def sqlComment(self, schema):
        return "comment on table %s.%s is\n'%s';\n\n" % (schema.name, self.name, self.comment)

    
    def addColumns(self, columns):
        self.columns = [] if self.columns is None else self.columns
        
        if isinstance(columns, list):
            self.columns.extend(columns)
        elif isinstance(columns, column):
            self.columns.append(columns)

            
    def addKeyColumns(self, columns):
        self.keys = [] if self.keys is None else self.keys
        
        if isinstance(columns, list):
            self.keys.extend(columns)
        elif isinstance(columns, column):
            self.keys.append(columns)

    def addIndexes(self, indexes):
        self.indexes = [] if self.indexes is None else self.indexes
        
        if isinstance(indexes, list):
            self.indexes.extend(indexes)
        elif isinstance(indexes, index):
            self.indexes.append(index)

    def getColumns(self, names):
        """
        Returns a list of column objects present in the table based on plain column names.
        """
        
        names = names if isinstance(names, list) else [names]
        return [i for i in self.columns if i.name in names]
            
    def primaryKey(self, schema, name=None):
        if self.keys is not None:
            keys = ", ".join([i.name for i in self.keys])
            return "alter table %s.%s\nadd constraint %s\nprimary key(%s);\n\n" % \
              (schema.name, self.name, "%s_%s_pkey" % (schema.name, self.name) if name is None else name, keys)

        return ""

    def createIndexes(self, schema):
        if self.indexes is not None:
            idx = [i.create(schema, self) for i in self.indexes]
            return "".join(idx)

        return ""
                      
    def create(self, schema):
        out = "create table %s.%s(\n" % (schema.name, self.name)
        out += ",\n".join(["  %s" % i.create() for i in self.columns])
        out += "\n);\n\n"
        
        return out

    def columnComments(self, schema):
        comments = [i.sqlComment(schema, self) for i in self.columns]
        return "".join(comments)

    def fullCreate(self, schema):
        return \
            self.codeComment()+ \
            self.create(schema)+ \
            self.alterOwner(schema)+ \
            self.primaryKey(schema)+ \
            self.createIndexes(schema)+self.sqlComment(schema)+ \
            self.columnComments(schema)


    def mkdocs(self):
        s = \
          "## Table %s\n\n" % self.name + \
          "%s\n\n" % self.comment + \
          "- owner: %s\n\n" % self.owner + \
          "__Columns:__\n\n| Name | Type | Comment |\n| ---- | ---- | ------- |\n"

        for c in self.columns:
            s += c.mkdocs()

        s += "\n"
        
        return s





# ----------
# View class
# ----------

class View(DbObject):
    """
    View.
    """
    
    def __init__(self, apogee, name, comment, sql=None, materialized=False, columns=None, indexes=None, owner=None):
        """
        Regarding columns, at least those used for indexes building must be present.
        """
        
        self.name = name
        self.sql = sql
        self.comment = comment
        self.materialized = materialized
        
        # Process columns, must end in a list
        if columns is not None:
            self.columns = columns if isinstance(columns, list) else [columns]

        # Process index definitions
        if indexes is not None:
            self.indexes = indexes if isinstance(indexes, list) else [indexes]
            
            if self.indexes<>[]: 
                for i in range(0, len(self.indexes)):
                    self.indexes[i] = Index(iType=self.indexes[i][0], columns=self.getColumns(self.indexes[i][1]),
                                            name=self.indexes[i][2] if len(self.indexes[i])==3 else None)

        # Process owner
        if owner is not None:
            self.owner = owner

        DbObject.__init__(self, apogee, name, comment)

            
    def refresh(self, schema):
        """
        Refreshes a materialized view.

        :param schema: The schema of the view.
        :type schema: apogee.core.schema
        """
        return "refresh materialized view %s.%s;\n\n" % (schema.name, self.name) if self.materialized \
          else ""

          
    def alterOwner(self, schema, newowner=None):
        newowner = newowner if newowner else self.owner
        newowner = self.apogee.getFromCatalog(newowner)
        schema = self.apogee.getFromCatalog(schema) if isinstance(schema, str) else schema        
        return "alter %sview %s.%s owner to %s;\n\n" % (
            "materialized " if self.materialized else "",
            schema.name, self.name, newowner.name)

    
    def codeComment(self):
        return Comment.comment(self.comment)

    def sqlComment(self, schema):
        return "comment on %sview %s.%s is\n'%s';\n\n" % (
            "materialized " if self.materialized else "",
            schema.name, self.name, self.comment)

    def addColumns(self, columns):
        self.columns = [] if self.columns is None else self.columns
        
        if isinstance(columns, list):
            self.columns.extend(columns)
        elif isinstance(columns, column):
            self.columns.append(columns)

    def addIndexes(self, indexes):
        self.indexes = [] if self.indexes is None else self.indexes
        
        if isinstance(indexes, list):
            self.indexes.extend(indexes)
        elif isinstance(indexes, index):
            self.indexes.append(index)

    def getColumns(self, names):
        """
        Returns a list of column objects present in the table based on plain column names.
        """
        names = names if isinstance(names, list) else [names]
        return [i for i in self.columns if i.name in names]

    def createIndexes(self, schema):
        if self.indexes is not None:
            idx = [i.create(schema, self) for i in self.indexes]
            return "".join(idx)

        return ""
                      
    def create(self, schema):
        out = "create %sview %s.%s as\n" % ("materialized " if self.materialized else "", schema.name, self.name)
        out += self.sql.rstrip("\n")
        out += ";\n\n"
        
        return out

    
    def vacuum(self, schema):
        """
        Vacuum the view.
        """
        return "vacuum %s.%s;\n\n" % (schema.name, self.name)
    
    
    def columnComments(self, schema):
        if self.columns: 
            comments = [i.sqlComment(schema, self) for i in self.columns]
            return "".join(comments)
        else:
            return ""
        
    def fullCreate(self, schema):
        return \
            self.codeComment()+ \
            self.create(schema)+ \
            self.alterOwner(schema)+ \
            self.createIndexes(schema)+ \
            self.sqlComment(schema)+ \
            self.columnComments(schema)


    def mkdocs(self):
        s = \
          "## " + \
          ("Materialized " if self.materialized else "") + \
          "View %s\n\n" % self.name + \
          "%s\n\n" % self.comment + \
          "- owner: %s\n\n" % self.owner + \
          "__Columns:__\n\n| Name | Type | Comment |\n| ---- | ---- | ------- |\n"

        if self.columns is not None:
            for c in self.columns:
                s += c.mkdocs()

        s += "\n"
        
        return s
