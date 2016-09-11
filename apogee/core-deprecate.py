




    


# class Tablespace(object):
#     """
#     Tablespace object.
#     """

#     name = None
#     """Tablespace name."""

#     location = None
#     """Tablespace location."""

#     comment = None
#     """Tablespace comment."""
    
#     def __init__(self, name=None, location=None, comment=None):
#         """
#         Defines a new tablespace.

#         :param name: Name of the tablespace.
#         :type name: String
#         :param location: Location of the tablespace, optional.
#         :type location: String
#         """
#         self.name = name
#         self.location = location
#         self.comment = comment

#         tablespaces[self.name] = self


#     def mkdocs(self):
#         return "__Tablespace %s located at %s:__ %s" % (self.name, self.location, self.comment)




        
                                                    







    


# class Helpers(object):
#     """
#     Miscellaneous and helpers methods.
#     """

#     @staticmethod
#     def begin():
#         """
#         Returns a begin transaction command.
#         """
#         return "begin;\n\n"

    
#     @staticmethod
#     def commit():
#         """
#         Returns a commit transaction command.
#         """
#         return "commit;\n\n"


#     @staticmethod
#     def vacuum(analyze=False):
#         """
#         Performs a vacuum.

#         :param analyze: Performs a vacuum analyze if True. Defaults to False.
#         :type analyze: Boolean
#         """
#         return "vacuum%s;\n\n" % (" analyze" if analyze else "")


#     @staticmethod
#     def copy(schema, table, path, columns=None, delimiter="|", csv=True, header=True, quote='"',
#              fromto="from", encoding="utf-8", null="-"):
#         """
#         Returns a copy command.
        
#         :param schema: A schema object.
#         :type schema: apogee.core.Schema
#         :param table: A table object, or a String with simply the name of the table.
#         :type table: apogee.core.Table or String
#         :param path: Path to/from file.
#         :type path: String
#         :param columns: A list of columns defining the order they are found in the CSV. Optional.
#         :type columns: List of strings
#         :param delimiter: CSV delimiter. Defaults to '|'.
#         :type delimiter: String
#         :param csv: Wheter the file is a CSV. Defaults to True.
#         :type csv: Boolean
#         :param header: Wheter the file has a header. Defaults to True.
#         :type header: Boolean
#         :param quote: Quote character to be used. Defaults to '"'.
#         :type quote: String
#         :param fromto: Wheter the copy is a from or a to. Possible values are 'from' or 'to'. Defaults to 'from'.
#         :type fromto: String 'from' or 'to'
#         :param encoding: Encoding the export is in. Defaults to 'utf-8'.
#         :type encoding: String
#         :param null: Null character placeholder. Defaults to '-'.
#         :type null: String
#         """

#         out = "\copy %s.%s%s %s '%s'" % (schema.name,
#                                          table if isinstance(table, str) else table.name,
#                                          "("+", ".join(columns)+")" if columns else "",
#                                          fromto, path)

#         if csv or header or quote or encoding or null:
#             out+=" with %s %s %s %s %s %s\n\n" % ( \
#                 "delimiter '%s'" % delimiter if delimiter else "",
#                 "csv" if csv else "",
#                 "header" if header else "",
#                 "quote '%s'" % quote if quote else "",
#                 "encoding '%s'" % encoding if encoding else "",
#                 "null '%s'" % null if null else "")

#         return out


#     @staticmethod
#     def header(blockComment=None, echoDash=None):
#         """
#         Writes a standard header with a block code comment, an echo dash comment, and a connection.

#         :param blockComment: The initial block code comment. Optional.
#         :type blockComment: String
#         :param echoDash: The initial echo dash comment. Optional. If it's omitted and blockComment is set, then it is used.
#         :type echoDash: String
#         """

#         echoDash = echoDash if echoDash else (blockComment if blockComment else None)
        
#         return \
#             (Comment.block("Comienza: "+blockComment) if blockComment else "")+ \
#             (Comment.echoDash("Comienza: "+echoDash) if echoDash else "")

            
#     @staticmethod
#     def footer(echoDash=None):
#         """
#         Writes a standard footer with an echo dash comment and a connection.

#         :param echoDash: The final echo dash comment. Optional.
#         :type echoDash: String
#         """

#         return \
#             (Comment.echoDash("Termina: "+echoDash) if echoDash else "")


#     @staticmethod
#     def createFolder(names, path="."):
#         """
#         Creates a folder.

#         :param names: Names(s) of the new folder(s).
#         :type names: String or list of strings
#         :param path: Path to create the folder into. Optional. Defaults to ".".
#         :type path: String
#         """
#         names = names if isinstance(names, list) else [names]

#         for i in names:
#             if not os.path.exists(path+"/"+i):
#                 os.makedirs(path+"/"+i)


#     @staticmethod
#     def psqlExecute(files, path="."):
#         """
#         Insert an execute psql file(s) \i command.

#         :param files: File(s) to execute.
#         :type files: String or list of strings.
#         :param path: Path to the file. Optional. Defaults to ".".
#         :type path: String.
#         """
#         files = files if isinstance(files, list) else [files]
#         out = ""
        
#         for i in files:
#             out+="\i %s\n\n" % (path+"/"+i)

#         return out
    

#     @staticmethod
#     def getSnippet(file, tag="", path="static_snippets"):
#         """
#         Gets a whole file or selected lines into the script.

#         :param file: File to read lines from.
#         :type file: String
#         :param tag: Tag wrapping the intended block to be copied. In snippet, tags looks like -- -#-{tag}. Omit to copy the whole file, discarding any tag.
#         :type tag: String
#         :param path: Path containing the file. Defaults to 'static_snippets'.
#         :type path: String
#         """

#         f = open(path+"/"+file, "r")
#         line = f.readline()
#         inblock = False
#         out = ""

#         while line:
#             if tag=="":
#                 inblock=True
#             elif line=="-- -#-{%s}\n" % tag:
#                 if inblock==False:
#                     inblock=True
#                 else:
#                     break
            
#             if inblock:
#                 if line[:7]<>"-- -#-{":
#                     out+=line

#             line = f.readline()
            
#         return out.strip("\n")


#     @staticmethod
#     def template(template, substitutions):
#         """
#         Process the template with substitutions. Substitution variables are marked as {{mark}}.

#         :param template: Template string to process by substitutions.
#         :type template: String
#         :param substitutions: A dictionary with elements to substitute (keys) and substitutions (values).
#         :type substitutions: Dictionary
#         """

#         for k,v in substitutions.iteritems():
#             template = template.replace("{{%s}}" % k, v)

#         return template


#     @staticmethod
#     def newLine(n=1):
#         """
#         Inserts n new lines.

#         :param n: Number of new lines to insert, defaults to 1.
#         :type n: Integer
#         """

#         return "".join(["\n"]*2)


        

#     @staticmethod
#     def processCatalog(catalogName, configuration=None):
#         """
#         Process a catalog with an optional configuration file.
#         """
#         objs = Helpers.loadCatalog(catalogName, configuration=configuration)

#         print objs
#         print
#         print

#         # precedence of processing
#         precedence = ["Role", "Extension", "Database", "Table", "Schema", "Script"]

#         # Process items
#         for p in precedence:
#             for k,v in objs.iteritems():
#                 if k[0:len(p)+1]=="%s_" % p:
#                     globals()[p](**v)
                    
                
#         if "roles" in objs.keys():
#             for i in objs["roles"]:
#                 Role(**i)

#         if "tablespaces" in objs.keys():
#             """TODO"""
#             pass

#         if "extensions" in objs.keys():
#             for i in objs["extensions"]:
#                 Extension(**i)

#         if "databases" in objs.keys():
#             for i in objs["databases"]:
#                 Database(**i)
                
#         if "tables" in objs.keys():
#             for i in objs["tables"]:
#                 if "iterate" in i.keys():
#                     for k in i["iterate"]:
#                         dc = copy.deepcopy(i)
#                         Helpers.parseConf(dc, k, mark="_#")
#                         dc.pop("iterate", None)
#                         Table(**dc)
#                 else:
#                     Table(**i)

#         if "schemas" in objs.keys():
#             for i in objs["schemas"]:
#                 Schema(**i)




                
    
    




        

            
# class Index(object):
#     """
#     Index.
#     """

#     name = None
#     """Name."""
    
#     iType = None
#     """Index type."""

#     columns = None
#     """Columns to index."""

#     def __init__(self, iType=None, columns=[], name=None):
#         self.name = name
#         self.iType = iType
#         self.columns = columns if isinstance(columns, list) else [columns]

#     def create(self, schema, table):
#         cols = [i.name for i in self.columns]
#         keys = ", ".join(cols)
#         name = self.name if self.name else "%s_%s_%s" % (table.name, "_".join(cols), self.iType)
        
#         return "create index %s\non %s.%s\nusing %s(%s);\n\n" % \
#           (name, schema.name, table.name, self.iType, keys)

                  

        
          
        


    
# class Column(object):
#     """
#     Column object.
#     """

#     name = None
#     """Column name."""

#     type = None
#     """Column type."""

#     comment = None
#     """Column comment."""

#     def __init__(self, name=None, type=None, comment=None):
#         self.name = name
#         self.type = type
#         self.comment = comment

        
#     def create(self):
#         return "%s %s" % (self.name, self.type)

#     def sqlComment(self, schema, table):
#         if self.comment is not None:
#             return "comment on column %s.%s.%s is\n'%s';\n\n" % (schema.name, table.name, self.name, self.comment)
#         else:
#             return ""

#     def mkdocs(self):
#         return "| %s | %s | %s |\n" % (self.name, self.dataType, self.comment)

        


# # TODO: ADD PRIVILEGES TO views and tables



    


# # Documentation writer

# class DocumentationWriter(object):
#     """
#     Documentation writer.
#     """

#     sitePath = None
#     """Path to the root of the scripts."""

#     mkdocsPath = None
#     """Path to the MkDocs folder."""

#     docName = None
#     """Name of the documentation."""
    
#     def __init__(self, docName, welcome, path):
#         self.sitePath = path
#         self.mkdocsPath = path+"/MkDocs"
#         self.docName = docName

#         # MkDocs folder creation
#         try:
#             distutils.dir_util.remove_tree(self.mkdocsPath)
#         except:
#             pass

#         # Initialize MkDocs
#         call("cd %s ; mkdocs new MkDocs" % self.sitePath, shell=True)

#         # Rewrite index.md
#         f = open(self.mkdocsPath+"/docs/index.md", "w")
#         f.write(welcome)
#         f.close()
                
#         # Configure it
#         f = open(self.mkdocsPath+"/mkdocs.yml", "w")
#         f.write("site_name: %s\n" % self.docName)
#         f.write("theme: yeti\n")
#         f.write("pages:\n")
#         f.write("- Home: index.md\n")
#         f.close()

        
#     def __sanitizeTitle(self, title):
#         """
#         Gets a clean file name from a title.
#         """
#         name = title
        
#         for t in [(" ", "-"), (",","")]:
#             name = name.replace(t[0], t[1])

#         return name
    
        
#     def addDocsGroup(self, title):
#         """
#         Adds a docs group.
#         """
#         f = open(self.mkdocsPath+"/mkdocs.yml", "a")
#         f.write("- %s:\n" % title)
#         f.close()
        
        
#     def addPage(self, title, objects, grouped=False, content=None):
#         """
#         Adds a documentation page.

#         objects: List of objects to document.
#         grouped: If the page is to be grouped with the last group created (order matters!!!)
#         title: Page title. File name will be a sanitation of title.
#         fileName: File name.
#         content: Additional starting content.
        
#         """
#         fileName = self.__sanitizeTitle(title)
        
#         f = open(self.mkdocsPath+"/docs/"+fileName+".md", "w")
        
#         if content:
#             f.write(content+"\n")

#         for i in objects:
#             st = i.mkdocs()
            
#             if st is not None:
#                 f.write(st)
            
#         f.close()

#         f = open(self.mkdocsPath+"/mkdocs.yml", "a")
#         f.write( \
#             ("    " if grouped else "") + \
#             "- %s: %s.md\n" % (title, fileName))
#         f.close()
        
        
