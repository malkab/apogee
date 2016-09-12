#!/usr/bin/env python
# coding=UTF8

"""

  Database configuration

"""

# Globals

gridNames = ["250", "125", "62_5", "31_25"]


# Local testing

localhost_catastro_puebla = {
    "host": "localhost",
    "port": "5435",

    # Users
    "role_super": "postgres",
    "role_super_pass": "postgres",

    "role_catastro_users": "catastro_users",
    
    "role_catastro_admin": "catastro_admin",
    "role_catastro_admin_pass": "catastro_admin",

    "role_catastro_op": "catastro_op",
    "role_catastro_op_pass": "catastro_op",

    "role_geoserver": "geoserver",
    "role_geoserver_pass": "geoserver",

    # Database names
    "superdb": "postgres",
    "db": "catastro_puebla",
    "tablespace": None,
    
    # Data export and import
    "test_municipios": "'41078'",
    "data_path": "/home/git/phd/Database/csv/catastro_puebla",

    "test_data_extraction_path": "/home/git/phd/Database/csv/Test_Data_Extraction",
    "scripts_generation_path": "/home/git/phd/Database/apogee-localhost_catastro_puebla"
}

localhost_catastro_test = {
    "host": "localhost",
    "port": "5435",

    # Users
    "role_super": "postgres",
    "role_super_pass": "postgres",

    "role_catastro_users": "catastro_users",
        
    "role_catastro_admin": "catastro_admin",
    "role_catastro_admin_pass": "catastro_admin",

    "role_catastro_op": "catastro_op",
    "role_catastro_op_pass": "catastro_op",

    "role_geoserver": "geoserver",
    "role_geoserver_pass": "geoserver",
    
    # Database names
    "superdb": "postgres",
    "db": "catastro_test",
    "tablespace": None,    
    
    # Data export and import
    "test_municipios": "'41091', '41078', '04066', '11015'",
    "data_path": "/home/git/phd/Database/csv/catastro_test",

    "test_data_extraction_path": "/home/git/phd/Database/csv/Test_Data_Extraction",
    "scripts_generation_path": "/home/git/phd/Database/apogee-localhost_catastro_test"
}

localhost_catastro = {
    "host": "localhost",
    "port": "5435",

    # Users
    "role_super": "postgres",
    "role_super_pass": "postgres",

    "role_catastro_users": "catastro_users",
        
    "role_catastro_admin": "catastro_admin",
    "role_catastro_admin_pass": "catastro_admin",

    "role_catastro_op": "catastro_op",
    "role_catastro_op_pass": "catastro_op",

    "role_geoserver": "geoserver",
    "role_geoserver_pass": "geoserver",
    
    # Database names
    "superdb": "postgres",
    "db": "catastro",
    "tablespace": None,    
    
    # Data export and import
    "test_municipios": "'41091', '41078', '04066', '11015'",
    "data_path": "/home/git/phd/Database/csv/catastro",

    "test_data_extraction_path": "/home/git/phd/Database/csv/Test_Data_Extraction",
    "scripts_generation_path": "/home/git/phd/Database/apogee-localhost_catastro"
}


    
# viv3.cica.es  

viv3_catastro_puebla = {
    "host": "viv3.cica.es",
    "port": "5454",

    # Users
    "role_super": "u3i2o3k2jfr32",
    "role_super_pass": "JU32kjes32ke0U2L2",

    "role_catastro_users": "catastro_users",
        
    "role_catastro_admin": "catastro_admin",
    "role_catastro_admin_pass": "ert212003",

    "role_catastro_op": "catastro_op",
    "role_catastro_op_pass": "CATastro2212",

    "role_geoserver": "geoserver_op",
    "role_geoserver_pass": "ESEtiPOdEProfesiOnAL1121",
    
    # Database names
    "superdb": "postgres",
    "db": "scandal_puebla",
    "tablespace": None,    
    
    # Data export and import
    "test_municipios": "'41091', '41078', '04066', '11015'",
    "data_path": "/data/Scandal/csv/catastro_puebla",

    "test_data_extraction_path": "/data/Scandal/csv/Test_Data_Extraction",
    "scripts_generation_path": "/home/git/phd/Database/apogee-viv3_catastro_puebla"
}


    
viv3_catastro_test = {
    "host": "viv3.cica.es",
    "port": "5454",

    # Users
    "role_super": "u3i2o3k2jfr32",
    "role_super_pass": "JU32kjes32ke0U2L2",

    "role_catastro_users": "catastro_users",
        
    "role_catastro_admin": "catastro_admin",
    "role_catastro_admin_pass": "ert212003",

    "role_catastro_op": "catastro_op",
    "role_catastro_op_pass": "CATastro2212",

    "role_geoserver": "geoserver_op",
    "role_geoserver_pass": "ESEtiPOdEProfesiOnAL1121",
    
    # Database names
    "superdb": "postgres",
    "db": "scandal_test",
    "tablespace": None,    
    
    # Data export and import
    "test_municipios": "'41091', '41078', '04066', '11015'",
    "data_path": "/data/Scandal/csv/catastro_test",

    "test_data_extraction_path": "/data/Scandal/csv/Test_Data_Extraction",
    "scripts_generation_path": "/home/git/phd/Database/apogee-viv3_catastro_test"
}

        

viv3_catastro = {
    "host": "viv3.cica.es",
    "port": "5454",

    # Users
    "role_super": "postgres",
    "role_super_pass": "V1v13_d43pg;-)",

    "role_catastro_users": "catastro_users",
        
    "role_catastro_admin": "catastro_admin",
    "role_catastro_admin_pass": "ert212003",

    "role_catastro_op": "catastro_op",
    "role_catastro_op_pass": "CATastro2212",

    "role_geoserver": "geoserver_op",
    "role_geoserver_pass": "ESEtiPOdEProfesiOnAL1121",
    
    # Database names
    "superdb": "postgres",
    "db": "scandal",
    "tablespace": "dataspace",    
    
    # Data export and import
    "test_municipios": "'41091', '41078', '04066', '11015'",
    "data_path": "/data/Scandal/csv/catastro",

    "test_data_extraction_path": "/data/Scandal/csv/Test_Data_Extraction",
    "scripts_generation_path": "/home/git/phd/Database/apogee-viv3_catastro"
}
    
