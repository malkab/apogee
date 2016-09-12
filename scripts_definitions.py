#!/usr/bin/env python
# coding=UTF8

import objects_definitions as d
import apogee.core as c


# ----------
# Get config
# ----------

conf = d.conf


# -------------
# Script writer
# -------------

f = c.ScriptWriter(conf["scripts_generation_path"])

c.Helpers.createFolder("builders", path=conf["scripts_generation_path"])
c.Helpers.createFolder("Lib_Geo", path=conf["scripts_generation_path"])


# --------------------
# Documentation writer
# --------------------

# ---------------------------
# 0010-Database_Roles-DDL.sql
# ---------------------------

orders = [
    c.Helpers.header(blockComment="Creación de base de datos y roles"),

    # Role creation
    c.Comment.block("Creación de usuarios y grupos"),
    
    "".join([i.fullCreate() for i in [d.role_catastro_users, d.role_catastro_admin, d.role_catastro_op, d.role_geoserver]]),

    # catastro DB creation
    c.Comment.block("Creación de la base de datos"),
    d.db_postgres.connect(),
    d.db_catastro.fullCreate(),
    d.db_catastro.connect(),
    d.db_catastro.createExtensions(),
    d.schema_public.alterOwner(d.role_catastro_admin),
    d.schema_public.sqlComment(),
    d.tb_public_spatial_ref_sys.sqlComment(d.schema_public),
    d.vw_public_geometry_columns.sqlComment(d.schema_public),
    d.vw_public_geography_columns.sqlComment(d.schema_public),
    d.vw_public_raster_columns.sqlComment(d.schema_public),
    d.vw_public_raster_overviews.sqlComment(d.schema_public),
    d.tb_public_spatial_ref_sys.alterOwner(d.schema_public, d.role_catastro_admin),
    d.vw_public_geometry_columns.alterOwner(d.schema_public, d.role_catastro_admin),
    d.vw_public_geography_columns.alterOwner(d.schema_public, d.role_catastro_admin),
    d.vw_public_raster_columns.alterOwner(d.schema_public, d.role_catastro_admin),
    d.vw_public_raster_overviews.alterOwner(d.schema_public, d.role_catastro_admin),
    d.role_public.revoke(d.schema_public, ["usage", "create"]),
    d.role_catastro_users.grant(d.schema_public, ["usage"]),
    d.role_catastro_users.grantOnAllTablesInSchema(d.schema_public, ["select"]),
    d.role_geoserver.grantOnAllTablesInSchema(d.schema_public, ["select"]),
    c.Comment.block("Finalizada la creación de la base de datos y roles")
]
    
f.render(orders, "0010-Database_Roles-DDL.sql")



# ----------------------------
# 0010-Database_Roles-Drop.sql
# ----------------------------

orders = [
    c.Helpers.header("Borrado de la base de datos y roles"),
    c.Comment.echo("Dropping database"),
    d.db_catastro.drop(),
    c.Comment.echo("Dropping roles"),
    "".join([i.drop() for i in [d.role_catastro_users, d.role_catastro_admin, d.role_catastro_op, d.role_geoserver]]),
    c.Helpers.footer(echoDash="Finalizado el borrado de la base de datos y roles.")]
    
f.render(orders, "0010-Database_Roles-Drop.sql")



# ------------------------------
# 0030-Context-00-Schema-DDL.sql
# ------------------------------

orders = [
    d.schema_context.fullCreate("Creación del esquema para datos de contexto.",
                              "Creación del esquema de datos de contexto")
]

f.render(orders, "0030-Context-00-Schema-DDL.sql")



# -------------------------------
# 0030-Context-00-Schema-Drop.sql
# -------------------------------

orders = [
    c.Comment.block("Borrado del esquema context de contexto"),
    c.Helpers.begin(),
    d.schema_context.drop(cascade=True),
    c.Helpers.commit(),
    c.Comment.block("Finalizado borrado del esquema context de contexto")
]

f.render(orders, "0030-Context-00-Schema-Drop.sql")



# -------------------------------
# 0030-Context-10-Data_import.sql
# -------------------------------

orders = [
    c.Comment.block("Importación de datos de contexto."),
    c.Comment.echoDash("Importación de datos de contexto"),
    d.db_catastro.connect(),
    c.Helpers.begin()
]

orders.extend([c.Helpers.copy(d.schema_context, d.gridTables[i],
    conf["data_path"]+"/Context/Grid_etrs89_30n_and_%sm.csv" % d.gridSuffix[i]) \
    for i in range(0,4)])

orders.append(c.Helpers.copy(d.schema_context, d.tb_context_municipio, conf["data_path"]+"/Context/Municipios.csv"))

orders.extend([
    c.Helpers.commit(),
    d.db_catastro.connect(),
    c.Comment.echoDash("Finalizada importación de datos de contexto")])
          
f.render(orders, "0030-Context-10-Data_import.sql")



# --------------------------------
# 0030-Context-20-Process_data.sql
# --------------------------------

orders = [
    c.Helpers.header("Procesamiento de datos de contexto"),
    c.Helpers.begin()
]

orders.extend(
    [i.refresh(d.schema_context) for i in d.centroidMViews])

orders.extend([
    c.Helpers.commit(),
    c.Helpers.vacuum(True),
    c.Helpers.footer("Final del procesamiento de datos de contexto")])
    
f.render(orders, "0030-Context-20-Process_data.sql")



# ------------------------------
# 0040-Fase_0-00-Schema-DDL.sql
# ------------------------------

orders = [
    d.schema_fase_0.fullCreate("Definición del esquema fase_0 que guarda los datos válidos de la fase 0 del proyecto de Vivienda.",
                              "Definición del esquema fase_0")
]

f.render(orders, "0040-Fase_0-00-Schema-DDL.sql")



# -------------------------------
# 0040-Fase_0-00-Schema-Drop.sql
# -------------------------------

orders = [
    d.schema_fase_0.fullDrop("Borrado del esquema fase_0 que guarda los datos válidos de la fase 0 del proyecto de Vivienda.",
                            "Borrado del esquema fase_0")
]

f.render(orders, "0040-Fase_0-00-Schema-Drop.sql")



# -------------------------------
# 0040-Fase_0-10-Data_import.sql
# -------------------------------

orders = [
    c.Helpers.header("Importación de datos de la fase 0"),
    c.Helpers.begin(),
    c.Helpers.copy(d.schema_fase_0, d.tb_fase_0_catastro_normalized_import_20150330__constru,
                conf["data_path"]+"/Fase_0/viv3_5454_catastro/catastro_normalized_import_20150330__constru.csv"),
    c.Helpers.copy(d.schema_fase_0, d.tb_fase_0_catastro__c_parcelas_andalucia,
                conf["data_path"]+"/Fase_0/viv3_5455_e_iberv/catastro__c_parcelas_andalucia.csv",
                columns=["refcat", "mun_refc", "tipo", "ipc_4", "df_1", "df_2", "df_3", "df_4", "pu001", "pu002", "pu003", "pu004", "pu005", "pu006", "pu007", "pu008", "pu009", "pu010", "pu011", "pu012", "pu013", "pu014", "pu015", "pu016", "pu017", "pu018", "pu019", "pu020", "pu021", "pu022", "pu023", "pu024", "pu025", "pu026", "pu027", "pu028", "pu029", "dt_1", "dt_2", "dt_3", "dt_4", "dt_5", "dt_6", "dt_7", "dt_8", "dt_9", "dt_10", "dt_11", "dt_12", "dt_13", "dt_14", "dt_15", "dt_17", "dt_18", "dt_19", "dt_20", "dt_21", "dt_22", "dt_23", "dt_24", "dt_25", "geom", "parcela", "gid", "cod_ine"]),
    c.Helpers.commit(),
    c.Helpers.vacuum(True),
    c.Helpers.footer("Finalizada la importación de datos de la fase 0")]

f.render(orders, "0040-Fase_0-10-Data_import.sql")



# -------------------------------------
# 0040-Fase_0-20-Extract_test_data.sql
# -------------------------------------



# -----------------------
# 0042-Load_Libraries.sql
# -----------------------

orders = [
    c.Helpers.header(
        "Carga de librerías de apoyo, procedentes del submódulo Geographica-PostGIS-Extensions"),
        c.Helpers.psqlExecute(["Lib_Geo/Vector.sql", "Lib_Geo/Geometries.sql", "Lib_Geo/Strings.sql",
                               "Lib_Geo/Array.sql"])]

f.render(orders, "0042-Load_Libraries.sql")



# -------------------------------------------------
# 0047-Procesamiento_base-00-Materialized_views.sql
# -------------------------------------------------

orders = [
    d.schema_procesamiento_base.fullCreate(
        blockComment="Procesamiento base de la información de catastro",
        echoComment="Procesamiento base de la información de catastro")]
        
f.render(orders, "0047-Procesamiento_base-00-Materialized_views.sql")



# -----------------------------------
# 0047-Procesamiento_base-10-Drop.sql
# -----------------------------------

orders = [
    d.schema_procesamiento_base.fullDrop("Borrado del esquema de procesamiento base.",
                                         "Borrado del esquema de procesamiento base.")]

f.render(orders, "0047-Procesamiento_base-10-Drop.sql")



# ------------------------------------
# 0050-agregaciones_rejilla-00-DDL.sql
# ------------------------------------

orders = [
    d.schema_agregaciones_rejilla.fullCreate(
        blockComment="Esquema agregaciones_rejilla que recoge diversas agrupaciones de indicadores a los distintos niveles de rejilla disponibles.",
        echoComment="Creación del esquema agregaciones_rejilla")]

f.render(orders, "0050-agregaciones_rejilla-00-DDL.sql")



# -------------------------------------
# 0050-agregaciones_rejilla-00-Drop.sql
# -------------------------------------

orders = [
    d.schema_agregaciones_rejilla.fullDrop("Borrado del esquema agregaciones_rejilla.",
                                           "Borrado del esquema agregaciones_rejilla.")]

f.render(orders, "0050-agregaciones_rejilla-00-Drop.sql")



# ---------------------------------------------
# 0050-agregaciones_rejilla-10-Process_data.sql
# ---------------------------------------------

orders = [d.schema_agregaciones_rejilla.fullRefresh()]

f.render(orders, "0050-agregaciones_rejilla-10-Process_data.sql")



# --------------------------------------
# 0060-inundable_costa-00-Schema-DDL.sql
# --------------------------------------

orders = [
    d.schema_inundable_costa.fullCreate(
        blockComment="Creación del esquema de afección por inundabilidad",
        echoComment="Creación del esquema de afección por inundabilidad")]

f.render(orders, "0060-inundable_costa-00-Schema-DDL.sql")



# ---------------------------------------
# 0060-inundable_costa-00-Schema-Drop.sql
# ---------------------------------------

orders = [
    d.schema_inundable_costa.fullDrop(
        "Borrado del esquema de inundabilidad.",
        "Borrado del esquema de inundabilidad.")]

f.render(orders, "0060-inundable_costa-00-Schema-Drop.sql")



# ---------------------------------------
# 0060-inundable_costa-10-Import_data.sql
# ---------------------------------------

orders = [
    c.Helpers.copy(
        d.schema_inundable_costa, d.tb_inundable_costa_inundable_costa,
        conf["data_path"]+"/inundable_costa/inundable_costa.csv"),
    d.schema_inundable_costa.fullRefresh()]

f.render(orders, "0060-inundable_costa-10-Import_data.sql")


# -------------------------------------
# 9000-Extract_test_data.sql
# -------------------------------------

orders = [
    c.Helpers.header("Extracción de datos de ejemplo de datos del esquema context"),
    d.schema_test_data.fullCreate(blockComment="Creación del esquema para almacenar los datos de ejemplo."),
    c.Helpers.begin(),
    c.Helpers.template(c.Helpers.getSnippet("0030-Context-30-Extract_test_data.sql"), {"test_municipios": conf["test_municipios"]}),
    c.Helpers.commit(),
    c.Comment.comment("Exportación a CSV")
]

orders.extend([c.Helpers.copy(d.schema_test_data, "grid_%s" % i,
                           conf["test_data_extraction_path"]+"/"+"Grid_etrs89_30n_and_%sm.csv" % i, fromto="to")
                           for i in d.gridSuffix])

orders.extend([
    c.Helpers.copy(d.schema_test_data, "municipio",
        conf["test_data_extraction_path"]+"/Municipios.csv", fromto="to"),
    c.Helpers.footer("Finalizada extracción de datos de ejemplo de datos del esquema context")])

orders.extend([
    c.Helpers.header("Extracción de datos de test del esquema fase_0"),
    c.Helpers.begin(),
    c.Helpers.getSnippet("0040-Fase_0-20-Extract_data.sql"),
    c.Helpers.newLine(),
    c.Helpers.commit(),
    c.Comment.comment("Exportación a CSV"),
    c.Helpers.copy(d.schema_test_data, "catastro__c_parcela_residencial",
                conf["test_data_extraction_path"]+"/catastro__c_parcela_residencial.csv", fromto="to",
                columns=["refcat", "mun_refc", "tipo", "pu005", "pu029", "geom", "parcela", "origen", "gid"]),
    c.Helpers.copy(d.schema_test_data, "catastro__c_parcelas_andalucia",
                conf["test_data_extraction_path"]+"/catastro__c_parcelas_andalucia.csv", fromto="to",
                columns=["refcat", "mun_refc", "tipo", "ipc_4", "df_1", "df_2", "df_3", "df_4", "pu001", "pu002", "pu003", "pu004", "pu005", "pu006", "pu007", "pu008", "pu009", "pu010", "pu011", "pu012", "pu013", "pu014", "pu015", "pu016", "pu017", "pu018", "pu019", "pu020", "pu021", "pu022", "pu023", "pu024", "pu025", "pu026", "pu027", "pu028", "pu029", "dt_1", "dt_2", "dt_3", "dt_4", "dt_5", "dt_6", "dt_7", "dt_8", "dt_9", "dt_10", "dt_11", "dt_12", "dt_13", "dt_14", "dt_15", "dt_17", "dt_18", "dt_19", "dt_20", "dt_21", "dt_22", "dt_23", "dt_24", "dt_25", "geom", "parcela", "gid", "cod_ine"]),
    c.Helpers.copy(d.schema_test_data, "catastro_normalized_import_20150330__constru",
                conf["test_data_extraction_path"]+"/catastro_normalized_import_20150330__constru.csv", fromto="to"),
    c.Helpers.footer("Finalizada extracción de datos de test del esquema fase_0"),
    d.schema_test_data.fullDrop(blockComment="Borrado del esquema para almacenar los datos de ejemplo.")
    ])


f.render(orders, "9000-Extract_test_data.sql")



# ---------------
# Process statics
# ---------------

f.statics()
f.statics(folder="Lib_Geo", path="Lib_Geo")



# ------------
# Builder full
# ------------

orders = [
    c.Helpers.header(
        "Creación de la base de datos con importación de datos, con exportación de datos"),

    c.Comment.echo("Ejecutar desde el directorio base de scripts."),
        
    c.Helpers.psqlExecute(["0010-Database_Roles-DDL.sql",
                           "0030-Context-00-Schema-DDL.sql",
                           "0030-Context-10-Data_import.sql",
                           "0040-Fase_0-00-Schema-DDL.sql",
                           "0040-Fase_0-10-Data_import.sql",
                           "0042-Load_Libraries.sql",
                           "0045-Additional_Functions.sql",
                           "0047-Procesamiento_base-00-Materialized_views.sql",
                           "0050-agregaciones_rejilla-00-DDL.sql",
                           "0060-inundable_costa-00-Schema-DDL.sql",
                           "0060-inundable_costa-10-Import_data.sql"])]
    
f.render(orders, "builders/full.sql")



# --------------------
# Builder Drop schemas
# --------------------

orders = [
    c.Helpers.header(
        "Borrado de los esquemas sin borrar la base de datos."),
    c.Comment.echo("Ejecutar desde el directorio base de scripts."),
    c.Helpers.psqlExecute(["0030-Context-00-Schema-Drop.sql",
                           "0040-Fase_0-00-Schema-Drop.sql",
                           "0050-agregaciones_rejilla-00-Drop.sql",
                           "0060-inundable_costa-00-Drop.sql"])]

f.render(orders, "builders/drop_schema.sql")
