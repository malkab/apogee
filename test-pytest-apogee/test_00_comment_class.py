#!/usr/bin/env python
# coding=UTF-8

import apogee.core as apo
reload(apo)

"""
Tests for Comment class.
"""

class TestComment:
    """
    Tests for class Comment.
    """

    def test_Comment(self):
        assert apo.Comment.block("This is the comment")=="/*\n\n  This is the comment\n\n*/\n\n"

        assert apo.Comment.echoDash("This is the comment")=="\echo -------------------\n\echo This is the comment\n\echo -------------------\n\n"

        assert apo.Comment.echo("This is the comment")=="\echo This is the comment\n\n"

        assert apo.Comment.comment("This is the comment")=="-- This is the comment\n\n"

        assert apo.Comment.blank()=="\n"

        assert apo.Comment.blank(3)=="\n\n\n"

        
