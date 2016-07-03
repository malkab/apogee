#!/usr/bin/env python
# coding=UTF-8

import apogee.ex as ex
reload(ex)

class TestRole:
    """
    Tests for class Executable.
    """

    
    def test_Executable(self):
        """
        Tests the Executable class.
        """

        e = ex.Executable("Test-Data.test_script.py", "Test-Data.config.py", "config_1")

        # print "UU", e.getApogeeDefs()
        
        f = open("test-pytest-apogee/Result-Files/core_Comment_block", "r")
        # assert e.execute() == f.read()

        print e.execute()
