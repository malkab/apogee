#!/usr/bin/env python
# coding=UTF8

import os, distutils.dir_util, sys

class Tablespace(object):
    """
    Tablespace object.
    """

    name = None
    """Tablespace name."""

    location = None
    """Tablespace location."""
    
    def __init__(self, name, location=None):
        """
        Defines a new tablespace.

        :param name: Name of the tablespace.
        :type name: String
        :param location: Location of the tablespace, optional.
        :type location: String
        """
        self.name = name
        self.location = location


        
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
                                                    


class Extension(object):
    """
    Database extension.
    """

    name = None
    """Extension name. String."""

    def __init__(self, name):
        """
        Constructor.

        :param name: Extension name.
        :type name: String
        """
        
        self.name = name

    def create(self):
        """
        Returns the creation string for the extension.
        """
        return "create extension %s;\n\n" % self.name
    

            
class Database(object):
    """
    Database.
    """

    name = None
    """Database name."""
    
    host = None
    """Database host."""
    
    port = None
    """Port. String."""
    
    comment = None
    """Database comment."""
    
    owner = None
    """Database owner. A role instance."""
    
    permissions = None
    """Database permissions. List of tuples."""
    
    extensions = None
    """Database extensions. List of apogee.core.Extension."""
    
    tablespace = None
    """Database tablespace."""
    
        
    def __init__(self, name, host="localhost", port="5432", comment=None, owner=None, permissions=None, extensions=None, tablespace=None):
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
        
        self.name = name
        self.host = host
        self.port = str(port)
        self.comment = comment
        self.owner = owner
        self.permissions = permissions if isinstance(permissions, list) else \
            ([permissions] if permissions is not None else None)
        self.extensions = extensions if isinstance(extensions, list) else [extensions]
        self.tablespace=tablespace

            
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
        
        return "create database %s%s%s;\n\n" % \
          (self.name,
           " owner %s" % owner.name if owner else "",
           " tablespace %s" % self.tablespace.name if self.tablespace else "")

    
    def codeComment(self):
        """
        Returns the code comment for the database.
        """
        return Comment.comment(self.comment) if self.comment else ""


    def sqlComment(self):
        """
        Returns SQL comment statement for Database.
        """
        return "comment on database %s is\n'%s';\n\n" % (self.name, self.comment) if self.comment else ""
    

    def createPermissions(self):
        """
        Returns permissions creation for the database.
        """
        if self.permissions is not None:
            out = "".join([i[0](self, i[1]) for i in self.permissions])
        else:
            out = ""
            
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
            self.create(owner)+ \
            self.sqlComment()+ \
            self.createPermissions()

        return out

              
    def createExtensions(self):
        """
        Creates extensions for the database.
        """

        return "".join([i.create() for i in self.extensions]) if self.extensions<>[None] else ""
        
        
    def drop(self):
        return "drop database %s;\n\n" % self.name



class Helpers(object):
    """
    Miscellaneous and helpers methods.
    """

    @staticmethod
    def begin():
        """
        Returns a begin transaction command.
        """
        return "begin;\n\n"

    
    @staticmethod
    def commit():
        """
        Returns a commit transaction command.
        """
        return "commit;\n\n"


    @staticmethod
    def vacuum(analyze=False):
        """
        Performs a vacuum.

        :param analyze: Performs a vacuum analyze if True. Defaults to False.
        :type analyze: Boolean
        """
        return "vacuum%s;\n\n" % (" analyze" if analyze else "")


    @staticmethod
    def copy(schema, table, path, columns=None, delimiter="|", csv=True, header=True, quote='"',
             fromto="from", encoding="utf-8", null="-"):
        """
        Returns a copy command.
        
        :param schema: A schema object.
        :type schema: apogee.core.Schema
        :param table: A table object, or a String with simply the name of the table.
        :type table: apogee.core.Table or String
        :param path: Path to/from file.
        :type path: String
        :param columns: A list of columns defining the order they are found in the CSV. Optional.
        :type columns: List of strings
        :param delimiter: CSV delimiter. Defaults to '|'.
        :type delimiter: String
        :param csv: Wheter the file is a CSV. Defaults to True.
        :type csv: Boolean
        :param header: Wheter the file has a header. Defaults to True.
        :type header: Boolean
        :param quote: Quote character to be used. Defaults to '"'.
        :type quote: String
        :param fromto: Wheter the copy is a from or a to. Possible values are 'from' or 'to'. Defaults to 'from'.
        :type fromto: String 'from' or 'to'
        :param encoding: Encoding the export is in. Defaults to 'utf-8'.
        :type encoding: String
        :param null: Null character placeholder. Defaults to '-'.
        :type null: String
        """

        out = "\copy %s.%s%s %s '%s'" % (schema.name,
                                         table if isinstance(table, str) else table.name,
                                         "("+", ".join(columns)+")" if columns else "",
                                         fromto, path)

        if csv or header or quote or encoding or null:
            out+=" with %s %s %s %s %s %s\n\n" % ( \
                "delimiter '%s'" % delimiter if delimiter else "",
                "csv" if csv else "",
                "header" if header else "",
                "quote '%s'" % quote if quote else "",
                "encoding '%s'" % encoding if encoding else "",
                "null '%s'" % null if null else "")

        return out


    @staticmethod
    def header(blockComment=None, echoDash=None):
        """
        Writes a standard header with a block code comment, an echo dash comment, and a connection.

        :param blockComment: The initial block code comment. Optional.
        :type blockComment: String
        :param echoDash: The initial echo dash comment. Optional. If it's omitted and blockComment is set, then it is used.
        :type echoDash: String
        """

        echoDash = echoDash if echoDash else (blockComment if blockComment else None)
        
        return \
            (Comment.block("Comienza: "+blockComment) if blockComment else "")+ \
            (Comment.echoDash("Comienza: "+echoDash) if echoDash else "")

            
    @staticmethod
    def footer(echoDash=None):
        """
        Writes a standard footer with an echo dash comment and a connection.

        :param echoDash: The final echo dash comment. Optional.
        :type echoDash: String
        """

        return \
            (Comment.echoDash("Termina: "+echoDash) if echoDash else "")


    @staticmethod
    def createFolder(names, path="."):
        """
        Creates a folder.

        :param names: Names(s) of the new folder(s).
        :type names: String or list of strings
        :param path: Path to create the folder into. Optional. Defaults to ".".
        :type path: String
        """
        names = names if isinstance(names, list) else [names]

        for i in names:
            if not os.path.exists(path+"/"+i):
                os.makedirs(path+"/"+i)


    @staticmethod
    def psqlExecute(files, path="."):
        """
        Insert an execute psql file(s) \i command.

        :param files: File(s) to execute.
        :type files: String or list of strings.
        :param path: Path to the file. Optional. Defaults to ".".
        :type path: String.
        """
        files = files if isinstance(files, list) else [files]
        out = ""
        
        for i in files:
            out+="\i %s\n\n" % (path+"/"+i)

        return out
    

    @staticmethod
    def getSnippet(file, tag="", path="static_snippets"):
        """
        Gets a whole file or selected lines into the script.

        :param file: File to read lines from.
        :type file: String
        :param tag: Tag wrapping the intended block to be copied. In snippet, tags looks like -- -#-{tag}. Omit to copy the whole file, discarding any tag.
        :type tag: String
        :param path: Path containing the file. Defaults to 'static_snippets'.
        :type path: String
        """

        f = open(path+"/"+file, "r")
        line = f.readline()
        inblock = False
        out = ""

        while line:
            if tag=="":
                inblock=True
            elif line=="-- -#-{%s}\n" % tag:
                if inblock==False:
                    inblock=True
                else:
                    break
            
            if inblock:
                if line[:7]<>"-- -#-{":
                    out+=line

            line = f.readline()
            
        return out.strip("\n")


    @staticmethod
    def template(template, substitutions):
        """
        Process the template with substitutions. Substitution variables are marked as {{mark}}.

        :param template: Template string to process by substitutions.
        :type template: String
        :param substitutions: A dictionary with elements to substitute (keys) and substitutions (values).
        :type substitutions: Dictionary
        """

        for k,v in substitutions.iteritems():
            template = template.replace("{{%s}}" % k, v)

        return template


    @staticmethod
    def newLine(n=1):
        """
        Inserts n new lines.

        :param n: Number of new lines to insert, defaults to 1.
        :type n: Integer
        """

        return "".join(["\n"]*2)
    
                    

class Comment(object):
    """
    Comment class.
    """

    
    @staticmethod
    def block(comment):
        return "/*\n\n  %s\n\n*/\n\n" % comment

    
    @staticmethod
    def echoDash(comment):
        l = len(comment)
        dash = "-" * l
        return "\echo %s\n\echo %s\n\echo %s\n\n" % (dash, comment, dash)

    
    @staticmethod
    def echo(comment):
        return "\echo %s\n\n" % comment

    
    @staticmethod
    def comment(comment):
        return "-- %s\n\n" % comment

    
    @staticmethod
    def blank(n=1):
        return "\n" * n
    
    

class ScriptWriter(object):
    """
    Class to render scripts.
    """        

    basePath = None
    """Base path to drop files in."""

    
    def __init__(self, basePath=None):
        """
        Manage files and render scripts.

        :param basePath: The path to drop generated files in. Optional.
        :type basePath: String
        """
        
        self.basePath = basePath
        
        
    def render(self, commands, file, path=None):
        """
        Renders a set of commands to a file. Commands are basically strings generated by functions.

        :param commands: Set of commands to drop into the file.
        :type commands: A string or a list of strings
        :param file: Name of the file to be generated. Will be generated by default at the class basePath, if any.
        :type file: String
        :param path: A path to render the file in. Optional. If this nor the class basePath is set defaults to the current folder.
        :type path: String
        """
        path = path if path else (self.basePath if self.basePath else ".")        
                
        try: 
            os.makedirs(self.basePath)
        except:
            pass
            
        f = open(path+"/"+file, "w")

        f.write(Comment.block("File: %s" % file))
        f.write(Comment.echoDash("Running script file: %s" % file))
        
        for c in commands:
            f.write(c)

        f.write(Comment.echoDash("Run of script file ended: %s" % file))
        f.write(Comment.block("End of file: %s" % file))
            
        f.close()

        
    def statics(self, folder="statics", path=None):
        """
        Copy all static files to the generation folder.

        :param folder: Folder where the static files are in. Defaults to 'statics'. If not, it is relative to the src folder.
        :type folder: String
        :param path: Path to drop files into. Optional. If this nor the class basePath is set defaults to the current folder. If set, it is relative to the basePath.
        :type path: String
        """
        
        path = self.basePath+"/"+path if path else (self.basePath if self.basePath else ".")
        
        distutils.dir_util.copy_tree(folder, path)



class Schema(object):
    """
    Schema.
    """

    name = None
    """Schema name."""
    comment = None
    """Schema comment."""
    permissions = None
    """Schema permissions."""
    owner = None
    """Schema authorization role."""
    tables = None
    """Schema tables."""
    views = None
    """Schema views."""

        
    def __init__(self, name, comment=None, permissions=None, owner=None, tables=None, views=None):
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

        
    def drop(self, cascade=False):
        return "drop schema %s%s;\n\n" % (self.name, " cascade" if cascade else "")
        
    def codeComment(self):
        return Comment.comment(self.comment)
    
    def sqlComment(self):
        return "comment on schema %s is\n'%s';\n\n" % (self.name, self.comment)

    
    def fullRefresh(self):
        """
        Refreshes all materialized views in the schema.
        """
        
        out = Comment.block("Refresh materialized view for schema %s" % self.name)+ \
            Comment.echoDash("Starting: Refreshing materialized views for schema %s" % self.name)

        for i in self.views:
            if i.materialized:
                out += Comment.echo("Materializing view %s" % i.name)+ \
                  i.refresh(self)+ \
                  i.vacuum(self)

        out += Comment.echoDash("End: Refreshing materializing views for schema %s" % self.name)

        return out

    
    def create(self, owner=None):
        au = owner if owner else self.owner
        
        return "create schema %s%s;\n\n" % (self.name, \
                                            " authorization %s" % au.name if au else "")

    def alterOwner(self, owner):
        return "alter schema %s owner to %s;\n\n" % (self.name, owner.name)

    def createPermissions(self):
        out = "".join([i[0](self, i[1]) for i in self.permissions if i])
        return out

    def fullCreate(self, blockComment=None, echoComment=None):
        """
        Full render of the schema.

        blockComment: a string with the block comment.
        echoComment: a string with the echo comment. Starting: and End: will be prefixed. If None, equals blockComment if present.
        """

        echoComment = echoComment if echoComment else (blockComment if blockComment else "")
        
        out = \
          (Comment.block(blockComment) if blockComment else "")+ \
          (Comment.echoDash("Beginning: "+echoComment) if echoComment else "")+ \
          (Helpers.begin())+ \
          (self.codeComment())+ \
          (self.create())+ \
          (self.sqlComment())+ \
          (self.createPermissions())+ \
          ("".join([i.fullCreate(self) for i in self.tables if i]))+ \
          ("".join([i.fullCreate(self) for i in self.views if i]))+ \
          (Helpers.commit())+ \
          (Comment.echoDash("Ending: "+echoComment) if echoComment else "")

        return out

    
    def fullDrop(self, blockComment=None, echoComment=None):
        """
        Full drop of a schema.

        blockComment: a string with the block comment.
        echoComment: a string with the echo comment. Starting: and End: will be prefixed. Equals the blockComment if ommited.
        """

        echoComment = echoComment if echoComment else (blockComment if blockComment else "")
        
        return \
            (Comment.block(blockComment) if blockComment else "")+ \
            (Comment.echoDash("Beginning: "+echoComment) if echoComment else "")+ \
            (Helpers.begin())+ \
            (self.codeComment())+ \
            (self.drop(cascade=True))+ \
            (Helpers.commit())+ \
            (Comment.echoDash("Ending: "+echoComment) if echoComment else "")
        
        

class Index(object):
    """
    Index.
    """

    name = None
    """Name."""
    
    iType = None
    """Index type."""

    columns = None
    """Columns to index."""

    def __init__(self, iType, columns=[], name=None):
        self.name = name
        self.iType = iType
        self.columns = columns if isinstance(columns, list) else [columns]

    def create(self, schema, table):
        cols = [i.name for i in self.columns]
        keys = ", ".join(cols)
        name = self.name if self.name else "%s_%s_%s" % (table.name, "_".join(cols), self.iType)
        
        return "create index %s\non %s.%s\nusing %s(%s);\n\n" % \
          (name, schema.name, table.name, self.iType, keys)
        

        
class Table(object):
    """
    Table.
    """

    name = None
    """Table name."""
    comment = None
    """Table comment."""
    columns = None
    """Column collection."""
    keys = None
    """Key columns."""
    indexes = None
    """Indexes."""
    owner = None
    """Table owner."""

        
    def __init__(self, name, comment, columns=None, keys=None, indexes=None, owner=None):
        self.name = name
        self.comment = comment

        # Process columns, must end in a list
        if columns is not None:
            self.columns = columns if isinstance(columns, list) else [columns]

        # Process keys, in the end it must be a list of column instances
        if keys is not None:
            self.keys = self.getColumns(keys)

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


    def alterOwner(self, schema, owner=None):
        owner = owner if owner else self.owner

        return "alter table %s.%s owner to %s;\n\n" % (schema.name, self.name, owner.name)        

        
    def codeComment(self):
        return Comment.comment(self.comment)
    
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



    
class Column(object):
    """
    Column object.
    """

    name = None
    """Column name."""

    dataType = None
    """Column type."""

    comment = None
    """Column comment."""

    def __init__(self, name, dataType, comment=None):
        self.name = name
        self.dataType = dataType
        self.comment = comment

    def create(self):
        return "%s %s" % (self.name, self.dataType)

    def sqlComment(self, schema, table):
        if self.comment is not None:
            return "comment on column %s.%s.%s is\n'%s';\n\n" % (schema.name, table.name, self.name, self.comment)
        else:
            return ""


# TODO: ADD PRIVILEGES TO views and tables

class View(object):
    """
    View.
    """

    name = None
    """Table name."""
    comment = None
    """Table comment."""
    columns = None
    """Column collection."""
    indexes = None
    """Indexes."""
    owner = None
    """Table owner."""
    sql = None
    """SQL sentence to build the view."""
    materialized = None
    """States if it is a materialized view."""

    
    def __init__(self, name, comment, sql=None, materialized=False, columns=None, indexes=None, owner=None):
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

            
    def refresh(self, schema):
        """
        Refreshes a materialized view.

        :param schema: The schema of the view.
        :type schema: apogee.core.schema
        """
        return "refresh materialized view %s.%s;\n\n" % (schema.name, self.name) if self.materialized \
          else ""

                      
    def alterOwner(self, schema, owner=None):
        owner = owner if owner else self.owner
        
        return "alter %sview %s.%s owner to %s;\n\n" % (
            "materialized " if self.materialized else "",
            schema.name, self.name, owner.name)

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

