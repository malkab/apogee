#!/usr/bin/env python
# coding=UTF8

import os, distutils.dir_util, sys

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

    def __init__(self, name, password, group=False, nologin=False, inherit=True, inrole=None, comment=None):
        """
        Creates a new role.

        :param name: Name of the role.
        :type name: String
        :param password: Role password. 
        :type password: String
        :param group: If the role is a group. Defaults to False.
        :type group: Boolean
        :param nologin: If the role has login privilege or not. Defautls to False.
        :type nologin: Boolean
        :param inherit: If the role inherits privileges. Defaults to True.
        :type inherit: Boolean
        :param inrole: Parent role. Defaults to None.
        :type inrole: String
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
        if str(dbObject.__class__)=="<class 'pgbuild.core.Database'>":
            objType = "database"
        elif str(dbObject.__class__)=="<class 'pgbuild.core.Schema'>":
            objType = "schema"

        privileges = privileges if isinstance(privileges, list) else [privileges]            
        priv = ', '.join(privileges)

        return "revoke %s on %s %s from %s;\n\n" % (priv, objType, dbObject.name, self.name)

    def grant(self, dbObject, privileges):
        """
        Grant permissions on database object.
        """
        if str(dbObject.__class__)=="<class 'pgbuild.core.Database'>":
            objType = "database"
        elif str(dbObject.__class__)=="<class 'pgbuild.core.Schema'>":
            objType = "schema"

        privileges = privileges if isinstance(privileges, list) else [privileges]
        priv = ', '.join(privileges)

        return "grant %s on %s %s to %s%s;\n\n" % (priv, objType, dbObject.name, \
                                                    "group " if self.group else "", self.name)

    def grantOnAllTablesInSchema(self, dbObject, privileges):
        """
        Grant permissions on all tables of a schema.
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
    """Database extensions. List of pgbuild.core.extension."""
    
        
    def __init__(self, name, host, port, comment, owner=None, permissions=None, extensions=None):
        """
        Constructor.

        :param name: The name of the database.
        :type name: String
        :param name: Database host.
        :type name: String
        :param port: Database port.
        :type port: Integer or String
        :param comment: Database comment.
        :type comment: String
        :param owner: Database owner. Optional.
        :type owner: pgbuild.core.role
        :param permissions: A tuple or list of tuples containing grants or revokes. For example (role_whatever.grant, ["connect", "usage").
        :type permissions: Tuple or list of tuples
        :param extensions: A pgbuild.core.extension or list of such to create extensions into the database.
        :type extensions: pgbuild.core.extension or list of pgbuild.core.extension
        """
        
        self.name = name
        self.host = host
        self.port = str(port)
        self.comment = comment
        self.owner = owner
        self.permissions = permissions if isinstance(permissions, list) else [permissions]
        self.extensions = extensions if isinstance(extensions, list) else [extensions]

            
    def connect(self, role=None):
        """
        Outputs a \c command to the database for a given role. Default role is database owner, if any.

        :param role: Role to connect with.
        :type role: pgbuild.core.role
        """
        role = role if role is not None else (self.owner if self.owner is not None else None)
        
        out = "\c %s %s %s %s\n\n" % (self.name,
                                      role.name if role is not None else "",
                                      self.host if role is not None else "",
                                      self.port if role is not None else "")
        return out

    def create(self, owner=None):
        """
        Outputs database create string.

        :param owner: Owner of database. Optional. Defaults to the database owner, if any.
        :type owner: pgbuild.core.role
        """

        owner = owner if owner else (self.owner if self.owner else None)
        
        return "create database %s%s;\n\n" % (self.name,
                                          " owner %s" % owner.name if owner else "")

    
    def codeComment(self):
        return Comment.comment(self.comment)

    def createPermissions(self):
        out = "".join([i[0](self, i[1]) for i in self.permissions])
        return out
    
    def sqlComment(self):
        return "comment on database %s is\n'%s';\n\n" % (self.name, self.comment)

    
    def fullCreate(self, superuser=None, owner=None):
        """
        Full create output for database. Outputs a code comment, the create, a SQL comment, grants and revokes, and extensions.

        :param superuser: An optional superuser with privileges to create extensions, if any.
        :type superuser: pgbuild.core.role
        :param owner: An optional owner. Defaults to the database owner.
        :type owner: pgbuild.core.role
        """
        
        owner = owner if owner else (self.owner if self.owner else None)
        
        out = \
            self.codeComment()+ \
            self.create(owner)+ \
            (self.connect(superuser) if superuser else "")+ \
            self.sqlComment()+ \
            self.createPermissions()+ \
            ("".join([i.create() for i in self.extensions]) if self.extensions<>[None] else "")

        return out
          

    def drop(self):
        return "drop database %s;\n\n" % self.name



class Misc(object):
    """
    Miscellaneous methods.
    """

    @staticmethod
    def begin():
        return "begin;\n\n"
    
    @staticmethod
    def commit():
        return "commit;\n\n"


    @staticmethod
    def vacuum(analyze=False):
        """
        Performs a vacuum.

        :param analyze: Performs a vacuum analyze if True. Defaults to False.
        :type analyze: Boolean
        """
        
        return "vacuum%s;\n\n" % " analyze" if analyze else ""


    @staticmethod
    def copy(schema, table, path, columns=None, delimiter="|", csv=True, header=True, quote='"',
             fromto="from", encoding="utf-8", null="-"):
        """
        Returns a copy command.
        schema: a schema object
        table: a table object, or a String with simply the name of the table
        path: path to/from file
        :param columns: A list of columns defining the order they are found in the CSV. Optional.
        :type columns: List of strings
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
    def header(blockComment=None, db=None, role=None, echoDash=None):
        """
        Writes a standard header with a block code comment, an echo dash comment, and a connection.

        :param blockComment: The initial block code comment. Optional.
        :type blockComment: String
        :param db: Database to connect to. Optional.
        :type db: pgbuild.core.database
        :param role: The role for connecting to the database. Optional.
        :type role: pgbuild.core.role
        :param echoDash: The initial echo dash comment. Optional. If it's omitted and blockComment is set, then it is used.
        :type echoDash: String
        """

        echoDash = echoDash if echoDash else (blockComment if blockComment else None)
        
        return \
            (Comment.block(blockComment) if blockComment else "")+ \
            (Comment.echoDash(echoDash) if echoDash else "")+ \
            (db.connect(role) if db else "")

            
    @staticmethod
    def footer(echoDash=None, db=None, role=None):
        """
        Writes a standard footer with an echo dash comment and a connection.

        :param echoDash: The final echo dash comment. Optional.
        :type echoDash: String
        :param db: Database to connect to. Optional.
        :type db: pgbuild.core.database
        :param role: The role for connecting to the database. Optional.
        :type role: pgbuild.core.role
        """

        return \
            (db.connect(role) if db else "")+ \
            (Comment.echoDash(echoDash) if echoDash else "")


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
        Executes a psql file(s) with \i.

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
        :param tag: Tag wrapping the intended block to be copied. In snippet, tags looks like -#-{tag}. Omit to copy the whole file, discarding any tag.
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
            elif line=="-#-{%s}\n" % tag:
                if inblock==False:
                    inblock=True
                else:
                    break
            
            if inblock:
                if line[:4]<>"-#-{":
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
    
    

class Script(object):
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

        :param folder: Folder where the static files are in. Defaults to 'statics'.
        :type folder: String
        :param path: Path to drop files into. Optional. If this nor the class basePath is set defaults to the current folder.
        :type path: String
        """
        
        path = path if path else (self.basePath if self.basePath else ".")
        
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
        :type owner: pgbuild.core.role
        :param tables: Tables belonging to the schema.
        :type tables: pgbuild.core.table or list of those.
        :param views: Views belonging to the schema.
        :type views: pgbuild.core.view or list of those.
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
                  i.refresh(self)

        out += Comment.echoDash("End: Refreshing materializing views for schema %s" % self.name)+ \
          Misc.vacuum(True)
          
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

    def fullCreate(self, blockComment=None, echoComment=None, db=None, db_role=None):
        """
        Full render of the schema.

        blockComment: a string with the block comment.
        echoComment: a string with the echo comment. Starting: and End: will be prefixed. If None, equals blockComment if present.
        db: a database instance to connect to to perform the creation.
        db_role: a role to connect to the aforementioned database.
        """

        echoComment = echoComment if echoComment else (blockComment if blockComment else "")
        
        out = \
          (Comment.block(blockComment) if blockComment else "")+ \
          (Comment.echoDash("Beginning: "+echoComment) if echoComment else "")+ \
          (db.connect(db_role) if db and db_role else "")+ \
          (Misc.begin())+ \
          (self.codeComment())+ \
          (self.create())+ \
          (self.sqlComment())+ \
          (self.createPermissions())+ \
          ("".join([i.fullCreate(self) for i in self.tables if i]))+ \
          ("".join([i.fullCreate(self) for i in self.views if i]))+ \
          (Misc.commit())+ \
          (Comment.echoDash("Ending: "+echoComment) if echoComment else "")

        return out

    
    def fullDrop(self, blockComment=None, echoComment=None, db=None, db_role=None):
        """
        Full drop of a schema.

        blockComment: a string with the block comment.
        echoComment: a string with the echo comment. Starting: and End: will be prefixed. Equals the blockComment if ommited.
        db: database to connect to.
        db_role: role for connecting to the database.
        """

        echoComment = echoComment if echoComment else (blockComment if blockComment else "")
        
        return \
            (Comment.block(blockComment) if blockComment else "")+ \
            (Comment.echoDash("Beginning: "+echoComment) if echoComment else "")+ \
            (db.connect(db_role) if db and db_role else "")+ \
            (Misc.begin())+ \
            (self.codeComment())+ \
            (self.drop(cascade=True))+ \
            (Misc.commit())+ \
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

    def alterOwner(self, schema, owner):
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
        return self.codeComment()+self.create(schema)+self.primaryKey(schema)+ \
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
        :type schema: pgbuild.core.schema
        """
        return "refresh materialized view %s.%s;\n\n" % (schema.name, self.name) if self.materialized \
          else ""

                      
    def alterOwner(self, schema, owner):
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

    def columnComments(self, schema):
        comments = [i.sqlComment(schema, self) for i in self.columns]
        return "".join(comments)

    def fullCreate(self, schema):
        return self.codeComment()+self.create(schema)+ \
          self.createIndexes(schema)+self.sqlComment(schema)+ \
          self.columnComments(schema)