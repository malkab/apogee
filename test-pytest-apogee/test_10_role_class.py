#!/usr/bin/env python
# coding=UTF-8

import apogee.core as apo
reload(apo)

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

