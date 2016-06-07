#!/usr/bin/env python
# coding=UTF-8

# import unittest as t, time
import apogee.core as apo
reload(apo)

"""
Tests for class Role.
"""

class TestRole:
    """
    Tests for class Role.
    """

    def test_Role(self):
        role = apo.Role(name="admins", password="admins_pass")

        assert role.create()=="""create role admins with login inherit password 'admins_pass';\n\n"""
        assert role.drop()=="""drop role admins;\n\n"""
        assert role.fullCreate()=="""create role admins with login inherit password 'admins_pass';\n\n"""
        assert role.alterPassword("new_pass")=="""alter role admins password 'new_pass';\n\n"""
        assert role.codeComment()==""
        assert role.sqlComment()==""

        role2 = apo.Role("admin", "admin_pass", group=False, nologin=False, inherit=True, inrole=role, comment="This is the comment")

        assert role2.create()=="create role admin with login inherit in role admins password 'admin_pass';\n\n"
        assert role2.drop()=="drop role admin;\n\n"
        assert role2.fullCreate()=="""-- This is the comment

create role admin with login inherit in role admins password 'admin_pass';

comment on role admin is
'This is the comment';\n\n"""
        assert role2.alterPassword("new_pass")=="alter role admin password 'new_pass';\n\n"
        assert role2.codeComment()=="-- This is the comment\n\n"
        assert role2.sqlComment()=="comment on role admin is\n'This is the comment';\n\n"

        # ###TODO: revoke, grant, and grantOnAllTablesInSchema must be tested in another object        



class TestExtension:
    """
    Tests for class Extension.
    """

    def test_Extension(self):
        e0 = apo.Extension("postgis")
        assert e0.create()=="create extension postgis;\n\n"        

        

class TestDatabase:
    """
    Tests for class Database.
    """

    def test_Database(self):
        db0 = apo.Database("db0")

        owner = apo.Role("db_owner", password="owner_pass")
        
        pg_ext = apo.Extension("postgis")

        db1 = apo.Database("db1", host="what.ever.host", port="4323", comment="The comment!", owner=owner,
                           permissions=[(owner.grant, ["connect", "usage"]), (owner.revoke, ["create role"])],
                           extensions=pg_ext)

        assert db0.connect()=="\c db0\n\n"
        assert db1.connect()=="\c db1 db_owner what.ever.host 4323\n\n"
        assert db0.create()=="create database db0;\n\n"
        assert db0.create(owner)=="create database db0 owner db_owner;\n\n"
        assert db1.create()=="create database db1 owner db_owner;\n\n"
        assert db0.codeComment()==""
        assert db0.sqlComment()==""
        assert db1.codeComment()=="-- The comment!\n\n"
        assert db1.sqlComment()=="comment on database db1 is\n'The comment!';\n\n"
        assert db0.createPermissions()==""
        assert db1.createPermissions()=="grant connect, usage on database db1 to db_owner;\n\nrevoke create role on database db1 from db_owner;\n\n"

        
        
        
        

class TestHelpers:
    """
    Tests for class Misc.
    """

    def test_Helpers(self):
        db0 = apo.Database("db0")
        role = apo.Role(name="admin", password="pass")
        db1 = apo.Database("db1", owner=role)
        
        assert apo.Helpers.begin()=="begin;\n\n"
        assert apo.Helpers.commit()=="commit;\n\n"
        assert apo.Helpers.vacuum()=="vacuum;\n\n"
        assert apo.Helpers.vacuum(analyze=True)=="vacuum analyze;\n\n"

        ### TODO: Check for copy
        # print apo.Helpers.copy()

        assert apo.Helpers.header(blockComment="db0 block comment", db=db0, role=role, echoDash="db0 echo dash")=="""/*

  Comienza: db0 block comment

*/

\echo -----------------------
\echo Comienza: db0 echo dash
\echo -----------------------

\c db0 admin localhost 5432\n\n"""

        assert apo.Helpers.header(blockComment="db1 block comment", db=db1, echoDash="db1 echo dash")=="""/*

  Comienza: db1 block comment

*/

\echo -----------------------
\echo Comienza: db1 echo dash
\echo -----------------------

\c db1 admin localhost 5432\n\n"""

        assert apo.Helpers.footer(db=db0, role=role, echoDash="db0 echo dash")=="""\c db0 admin localhost 5432

\echo ----------------------
\echo Termina: db0 echo dash
\echo ----------------------\n\n"""

        assert apo.Helpers.footer(db=db1, echoDash="db1 echo dash")=="""\c db1 admin localhost 5432

\echo ----------------------
\echo Termina: db1 echo dash
\echo ----------------------\n\n"""




             
        ### TODO: Check createFolder
        ### TODO: Check psqlExecute

        assert apo.Helpers.getSnippet("Snippets-Example.sql", tag="municipios", path="Test-Data")=="""create table test_data.municipio as
select * from context.municipio
where cod_mun in ({{test_municipios}});"""

        assert apo.Helpers.getSnippet("Snippets-Example.sql", path="Test-Data")=="""-- Municipios test


create table test_data.municipio as
select * from context.municipio
where cod_mun in ({{test_municipios}});




-- Extracción de rejillas


create table test_data.grid_250 as
select
  a.*
from
  context.grid_250 a inner join
  test_data.municipio b on st_intersects(a.geom, b.geom);


create table test_data.grid_125 as
select
  a.*
from
  context.grid_125 a inner join
  test_data.municipio b on st_intersects(a.geom, b.geom);


create table test_data.grid_62_5 as
select
  a.*
from
  context.grid_62_5 a inner join
  test_data.municipio b on st_intersects(a.geom, b.geom);


create table test_data.grid_31_25 as
select
  a.*
from
  context.grid_31_25 a inner join
  test_data.municipio b on st_intersects(a.geom, b.geom);"""
                
        ### TODO: Check template
        ### TODO: Check newLine
