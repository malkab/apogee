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

    def test_role(self):
        role = apo.Role(name="admins", password="admins_pass")

        assert role.create()=="""create role admins with login inherit password 'admins_pass';\n\n"""
        assert role.drop()=="""drop role admins;\n\n"""
        assert role.fullCreate()=="""create role admins with login inherit password 'admins_pass';\n\n"""
        assert role.alterPassword(password="new_pass")=="""alter role admins password 'new_pass';\n\n"""
        assert role.codeComment()==""
        assert role.sqlComment()==""


        
