#!/usr/bin/env python
# coding=UTF8

from apogee.core import *


# This module should be passed to the executable as argument, as long as the config module and the config profile

# Import first the config module, take the config profile and put it in globals so they are visible here as "config"


helpers.createFolder("builders", path=conf["scripts_generation_path"])

Script.render(
    "0005-Database_Base_configuration-DDL.sql",
    [
        helpers.header(
            blockComment="Configura el superusuario.",
            db=d.db_postgres,
            role=d.role_postgres),
        role_postgres.alterPassword(),
        helpers.footer(
            echoDash="Configura el superusuario.",
            db=d.db_postgres,
            role=d.role_postgres)])
