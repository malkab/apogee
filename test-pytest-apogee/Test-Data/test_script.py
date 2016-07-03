#!/usr/bin/env python
# coding=UTF-8

import apogee.core as core
reload(core)

ap_example = {
    "method": core.Comment.block, 
    "comment": "This is an example"
}

role_super = {
    "class": core.Role,
    "name": config["super_name"],
    "password": config["super_password"]
}
        
ap_another = {
    "method": core.Comment.echoDash,
    "comment": "Another example"
}

script_0000_10_test = {
    "class": core.Script,
    "name": "0000-10-Test.sql",
    "basePath": ".",

    # All this items must have a method member and these methods must return a string
    "items": [ ap_example,
               ap_another,
               {"object": role_super, "method": core.Role.alterPassword}
             ]
}
