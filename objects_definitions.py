#!/usr/bin/env python
# coding=UTF8

import apogee.core as c
import config as config


# Get config
conf = config.localhost_catastro_test


# -----
# Roles
# -----

role_public = c.Role("PUBLIC", inherit=False)

role_postgres = c.Role(conf["role_super"], password=conf["role_super_pass"], comment="The superuser.")

role_catastro_users = c.Role(conf["role_catastro_users"], group=True, nologin=True, 
                             comment="Grupo de usuarios de la base de datos de catastro.")

role_catastro_admin = c.Role(conf["role_catastro_admin"], password=conf["role_catastro_admin_pass"],
                             inrole=role_catastro_users,
                             comment="Administrador y dueño de la base de datos de catastro.")

role_catastro_op = c.Role(conf["role_catastro_op"], password=conf["role_catastro_op_pass"],
                          inrole=role_catastro_users, 
                          comment="Operador de la base de datos de catastro.")

role_geoserver = c.Role(conf["role_geoserver"], password=conf["role_geoserver_pass"],  
                        comment="Usuario para acceso de GeoServer de la base de datos de catastro.")


# -----------
# Tablespaces
# -----------

if conf["tablespace"]:
    tablespace = c.Tablespace(conf["tablespace"])
else:
    tablespace = None

# ---------
# Databases
# ---------

db_postgres = c.Database(conf["superdb"], conf["host"], conf["port"], "The super DB.""")

db_catastro = c.Database(conf["db"], conf["host"], conf["port"],
                         "Base de datos principal de análisis de catastro.",
                         role_catastro_admin,
                         [(role_public.revoke, ["connect", "temp"]),
                          (role_catastro_users.grant, ["connect", "temp"]),
                          (role_geoserver.grant, ["connect"])],
                         c.Extension("postgis"),
                         tablespace=tablespace)

                         

# -------------
# Schema public
# -------------                          

schema_public = c.Schema("public", "Esquema público estándar. Contiene el esquema de la extensión PostGIS.")

tb_public_spatial_ref_sys = c.Table("spatial_ref_sys",
                                    "Tabla estándar PostGIS para almacenamiento de información de SRS.")

vw_public_geometry_columns = c.View("geometry_columns",
                                    "Vista estándar PostGIS para consulta de columnas geométricas.")

vw_public_geography_columns = c.View("geography_columns",
                                     "Vista estándar PostGIS para consulta de columnas geográficas.")

vw_public_raster_columns = c.View("raster_columns",
                                  "Vista estándar PostGIS para la consulta de columnas ráster.")

vw_public_raster_overviews = c.View("raster_overviews",
                                    "Vista estándar PostGIS para almacenar pirámides ráster.")

    

# --------------
# Schema context
# --------------

# Grids tables and materialized views

gridSuffix = ["250", "125", "62_5", "31_25"]
gridSizes = [250, 125, 62.5, 31.25]

gridTables = []
centroidMViews = []

for i in range(0, len(gridSuffix)):
    gridTables.append(
        c.Table(
            "grid_%s" % gridSuffix[i],
            "Rejilla de %s metros para Andalucía. Los códigos son heredados de la rejilla de referencia utilizada para su construcción, la de 250 metros del IECA (Instituto de Estadística y Cartografía de Andalucía), que a su vez se crea a partir de la rejilla oficial europea de 1 km." % gridSizes[i],
            [
                c.Column("gid", "bigint", "ID de la rejilla."),
                c.Column("grd_fixid", "varchar(27)", "Un código de la rejilla."),
                c.Column("grd_floaid", "varchar(23)", "Otro código de la rejilla."),
                c.Column("grd_inspir", "varchar(19)", "Otro código de la rejilla."),
                c.Column("geom", "geometry(POLYGON, 25830)", "Geometría de la rejilla, POLYGON, EPSG 25830.")
            ],
            "gid", ("gist", "geom"), role_catastro_admin))

    centroids = """select
  gid,
  grd_fixid,
  grd_floaid,
  grd_inspir,
  st_setsrid(st_centroid(geom), 25830) as geom
from
  context.grid_%s;""" % gridSuffix[i]

    centroidsCols = gridTables[0].getColumns(["gid", "grd_fixid", "grd_floaid", "grd_inspir"])
    centroidsCols.append(c.Column("geom", "geometry(POINT, 25830)", "Geometría del centroide de la rejilla, POINT, EPSG 25830."))
        
    centroidMViews.append(
        c.View(
            "mvw__grid_%s_centroid" % gridSuffix[i],
            "Vista materializada de los centroides de la rejilla de %s metros para Andalucía. Los códigos son heredados de la rejilla de referencia utilizada para su construcción, la de 250 metros del IECA (Instituto de Estadística y Cartografía de Andalucía), que a su vez se crea a partir de la rejilla oficial europea de 1 km." % gridSizes[i],
            centroids,
            materialized=True,
            columns=centroidsCols,
            indexes=[("btree", "gid"), ("gist", "geom")], owner=role_catastro_admin))
        
# Table context.municipio

tb_context_municipio = c.Table(
    "municipio",
    "Municipios según el DERA 2013 con una limpieza topológica de GRASS 7.",
    [
        c.Column("gid", "bigint", "Numérico identificador."),
        c.Column("cod_mun", "varchar(5)", "Código INE del municipio."),
        c.Column("municipio", "varchar(150)", "Nombre del municipio."),
        c.Column("provincia", "varchar(25)", "Nombre de la provincia."),
        c.Column("geom", "geometry(MULTIPOLYGON, 25830)",
            "Geometría multipoligonal del municipio en ETRS 89 UTM zona 30 norte.")],
    "gid", ("gist", "geom"), role_catastro_admin)
    
gridTables.append(tb_context_municipio)
        

# Schema

schema_context = c.Schema("context", "Esquema para datos de contexto.",
                          permissions=[(role_catastro_users.grant, "usage"), (role_geoserver.grant, "usage")],
                          owner=role_catastro_admin,
                          tables=gridTables,
                          views=centroidMViews)


        
# --------------
# Schema fase_0
# --------------

# Table fase_0.catastro_normalized_import_20150330__constru

tb_fase_0_catastro_normalized_import_20150330__constru = c.Table(
  "catastro_normalized_import_20150330__constru",
  "Capa de información legacy de la fase 0 del proyecto de Vivienda y Scandal que contiene las construcciones del catasto a fecha 2015-03-30. El esquema es el original de catastro y no se le ha realizado ningún tipo de operación de normalización ni alfanumérica ni topológica. La documentación de los campos corresponde a la original de catastro.",
  [
      c.Column("gid", "bigint", "ID único."),
      c.Column("pcat1", "varchar(7)", "Posiciones 1 a 7 de la referncia catastral de la parcela (varchar(7))."),
      c.Column("pcat2", "varchar(7)", "Posiciones 8 a 14 de la referencia catastral de la parcela (varchar(7))."),
      c.Column("mapa", "varchar(6)", "Número delete mapa al que pertenece la parcela (varchar(6))."),
      c.Column("delegacio", "varchar(2)", "Código de la Delegación de Hacienda a la que pertenece el elemento (varchar(2))."),
      c.Column("municipio", "varchar(3)", "Código del municipio (varchar(3))."),
      c.Column("masa", "varchar(5)", "Manzana urbana (o polígono rústico) a la que pertenece el elemento (varchar(5))."),
      c.Column("parcela", "varchar(5)", "Código de la parcela dentro de la manzana o polígono (varchar(5))."),
      c.Column("hoja", "varchar(7)", "Posiciones 8 a 14 de la referencia catastral (urbana) o código de sector (rústica) (varchar(7))."),
      c.Column("tipo", "varchar(1)", "Tipo de parcela (U, D, R) (varchar(1))."),
      c.Column("constru", "varchar(25)", "Rótulo con las alturas construidas y tipología. Ver el documento sobre el formato shapefile de catastro, anexos, para más detalles (varchar(16))."),
      c.Column("coorx", "double precision", "Coordenada X de un punto interior a la construcción (double precision)."),
      c.Column("coory", "double precision", "Coordenada Y de un punto interior a la construcción (double precision)."),
      c.Column("numsymbol", "varchar(2)", "Símbolo con el que se dibuja (para sombreados de colores) (varchar(2))."),
      c.Column("area", "double precision", "Superficie del elemento en metros cuadrados (double precision)."),
      c.Column("fechaalta", "varchar(8)", "Fecha de dibujo del elemento gráfico (varchar(8))."),
      c.Column("fechabaja", "varchar(8)", "Fecha de borrado del elemento gráfico (varchar(8))."),
      c.Column("ninterno", "varchar(10)", "Número secuencial asignado por el sistema de catastro. Desconocemos si es coherente en cada descarga o ejecución de exportación (varchar(10))."),
      c.Column("refcat", "varchar(14)", "Referencia catastro de la parcela (varchar(14))."),
      c.Column("catastrotype", "varchar(7)", "Filiación del elemento durante el proceso de importación a la base de datos de Scandal, según el tipo de shapefile desde el que el elemento fue importado (varchar(7))."),
      c.Column("packagepath", "varchar(100)", "Filiación del elemento durante el proceso de importación a la base de datos de Scandal, según la ruta del shapefile desde el que fue importado (varchar(100))."),
      c.Column("geom", "geometry (POLYGON, 25830)", "Geometría de la construcción en CRS ETRS89 UTM Zona 30 N (geometry(POLYGON, 25830)).")],
  "gid",
  ("gist", "geom"),
  role_catastro_admin)

# Table fase_0.catastro__c_parcela_residencial

# -----------------
# Esta tabla es sólo utilizada como base para catastro__c_parcelas_andalucia,
# que es la que tiene la carga de indicadores completa
# -----------------

tb_fase_0_catastro__c_parcela_residencial = c.Table(
    "catastro__c_parcela_residencial",
    'Tabla heredada de la fase 0 de Vivienda / Scandal que contiene las parcelas con algún uso residencial, con dos indicadores calculados TODO TODO: pu005, que son las BLABLABLA TODO, y pu029, que son BLABLABLA TODO TODO.',
    [
        tb_fase_0_catastro_normalized_import_20150330__constru.getColumns("gid")[0],
        tb_fase_0_catastro_normalized_import_20150330__constru.getColumns("refcat")[0],
        c.Column("mun_refc", "varchar(19)", 'Referencia catastral de la parcela, con el código municipal prefijado (varchar(19)).'),
        tb_fase_0_catastro_normalized_import_20150330__constru.getColumns("tipo")[0],
        c.Column("pu005", "integer", 'Indicador precalculado que indica, por parcela, el número de TODOTODO BLABLABLA (integer).'),
        c.Column("pu029", "integer", 'Indicador precalculado que indica, por parcela, el número de TODOTODO BLABLABLA (integer).'),
        tb_fase_0_catastro_normalized_import_20150330__constru.getColumns("parcela")[0],
        c.Column("origen", "varchar(7)", 'Origen de la parcela (rústico o urbano) (varchar(7)).'),
        c.Column("geom", "geometry(MULTIPOLYGON, 25830)", "Geometría de la parcela en CRS ETRS89 UTM Zona 30 N.")
    ],
    "gid",
    ("gist", "geom"),
    role_catastro_admin
)

# Table fase_0.catastro__c_parcelas_andalucia

cols = [
    c.Column("gid", "bigint", "Presunta clave primaria, pero tiene valores duplicados. Se utiliza un bigserial en gid_pkey."),
    c.Column("gid_pkey", "bigserial", "Esta es la clave primaria de compromiso."),
    c.Column("cod_ine", "varchar(5)", 'Código municipal del INE (varchar(5)).')]

cols.extend(tb_fase_0_catastro__c_parcela_residencial.getColumns(["parcela", "refcat", "mun_refc", "tipo"]))

# TODOTODO Comments here!

cols.extend([
            c.Column("ipc_4", "varchar(14)", None),
            c.Column("df_1", "integer", None),
            c.Column("df_2", "integer", None),
            c.Column("df_3", "integer", None),
            c.Column("df_4", "integer", None),
            c.Column("pu001", "integer", None),
            c.Column("pu002", "integer", None),
            c.Column("pu003", "integer", None),
            c.Column("pu004", "integer", None),
            c.Column("pu005", "integer", None),
            c.Column("pu006", "integer", None),
            c.Column("pu007", "integer", None),
            c.Column("pu008", "integer", None),
            c.Column("pu009", "integer", None),
            c.Column("pu010", "integer", None),
            c.Column("pu011", "integer", None),
            c.Column("pu012", "integer", None),
            c.Column("pu013", "integer", None),
            c.Column("pu014", "integer", None),
            c.Column("pu015", "integer", None),
            c.Column("pu016", "integer", None),
            c.Column("pu017", "integer", None),
            c.Column("pu018", "integer", None),
            c.Column("pu019", "integer", None),
            c.Column("pu020", "integer", None),
            c.Column("pu021", "integer", None),
            c.Column("pu022", "integer", None),
            c.Column("pu023", "varchar(1)", None),
            c.Column("pu024", "integer", None),
            c.Column("pu025", "integer", None),
            c.Column("pu026", "integer", None),
            c.Column("pu027", "integer", None),
            c.Column("pu028", "integer", None),
            c.Column("pu029", "integer", None),
            c.Column("dt_1", "integer", None),
            c.Column("dt_2", "varchar(50)", None),
            c.Column("dt_3", "integer", None),
            c.Column("dt_4", "integer", None),
            c.Column("dt_5", "varchar(50)", None),
            c.Column("dt_6", "varchar(50)", None),
            c.Column("dt_7", "integer", None),
            c.Column("dt_8", "varchar(50)", None),
            c.Column("dt_9", "varchar(50)", None),
            c.Column("dt_10", "integer", None),
            c.Column("dt_11", "varchar(50)", None),
            c.Column("dt_12", "integer", None),
            c.Column("dt_13", "varchar(50)", None),
            c.Column("dt_14", "integer", None),
            c.Column("dt_15", "varchar(50)", None),
            c.Column("dt_17", "varchar(50)", None),
            c.Column("dt_18", "integer", None),
            c.Column("dt_19", "integer", None),
            c.Column("dt_20", "integer", None),
            c.Column("dt_21", "integer", None),
            c.Column("dt_22", "integer", None),
            c.Column("dt_23", "integer", None),
            c.Column("dt_24", "integer", None),
            c.Column("dt_25", "varchar(50)", None),
            c.Column("geom", "geometry(POLYGON, 25830)", None)])

tb_fase_0_catastro__c_parcelas_andalucia = c.Table(
    "catastro__c_parcelas_andalucia",
    'Tabla de indicadores de las parcelas de Andalucía, heredada de la fase 0 de Vivienda / Scandal. Contiene una gran cantidad de indicadores resultados de los análisis de la primera fase del proyecto. Tiene problemas con la presunta clave primaria gid, que contiene valores duplicados. Ha sido substituida por una clave primaria de conveniencia gid_pkey, que es un bigserial.',
    cols,
    "gid_pkey",
    ("gist", "geom"),
    role_catastro_admin)

# Schema

schema_fase_0 = c.Schema("fase_0", "Esquema para almacenar en duro los resultados válidos de la primera fase del proyecto de Vivienda.", [(role_catastro_users.grant, "usage"), (role_geoserver.grant, "usage")], role_catastro_admin,
                          [tb_fase_0_catastro_normalized_import_20150330__constru,
                           tb_fase_0_catastro__c_parcelas_andalucia])



# ------------------------------------
# procesamiento_base schema definition
# ------------------------------------

views = []

template = c.Helpers.getSnippet("0047-Procesamiento_base-Materialized_views.sql", tag="constru")

mv = c.View("mvw__constru",
            "Estudio de construcciones, con diversas características adicionales, como por ejemplo el volumen calculado, la altura máxima, el parseo del campo constru, etc.",
            sql=template,
            materialized=True,
            columns=[
              c.Column("gid", "integer", "Clave primaria."),
              c.Column("constru", "varchar", "Campo con la tipología de construcción."),
              c.Column("parsedconstru", "gs__tokenizer", "Resultado de la tokenización del campo constru."),
              c.Column("altura", "integer", "Altura máxima en función del análisis de los token del campo constru."),
              c.Column("profundidad", "integer", "Profundidad bajo rasante en función del análisis de los token del campo constru."),
              c.Column("volumen", "double precision", "Volumen estimado de la construcción, tomando como planta promedio 3 metros, el campo altura y el área"),
              c.Column("geom", "geometry", "Geometría de la construcción.")],
            owner=role_catastro_admin,
            indexes=[("btree", "gid"), ("gist", "geom")])

views.append(mv)



template = c.Helpers.getSnippet("0047-Procesamiento_base-Materialized_views.sql", tag="template_c_aerea_parcelas")
            
mv = c.View("mvw__c_aerea_parcelas",
            "Estudio principal de construcciones susceptibles de contener viviendas incluidas en parcelas. El criterio para determinar la susceptibilidad de contener viviendas es ahora mismo que tengan una altura de plantas (un I, II, III en el campo constru, por ejemplo). Se agregan por parcelas las características de las parcelas cuyo centroide cae dentro de las mismas, calculándose en el proceso diversas magnitudes y geometrías: centroide de la parcela (p_centroid), número de construcciones en cada parcela (c_num_constru), total de área de construcciones en la parcela (c_total_area), total de volumen de construcciones en la parcela (teniendo en cuenta plantas estándar de 3 metros y las alturas obtenidas del parseo del campo constru, campo c_total_volumen), las geometrías individuales de la construcciones (c_individual_geoms), las construcciones dentro de la parcela como multipolígono (c_geoms), el conjunto individual de centroides de construcciones (c_centroids_array), los centroides de construcciones como multipunto (c_centroids), el porcentaje de cobertura de construcciones frente a la parcela (per_cobertura) y por último el centro de gravedad ponderado por área de construcción de los centroides de las mismas (area_centroide) y el centro de gravedad ponderado por volumen (volumen_centroide). Las parcelas tenidas en cuenta están filtradas con el criterio de no ser de tipo X (campo tipo), mientras que las construcciones lo están, como se ha dicho antes, por tener una altura deducida del parseo de su campo constru.",
            sql=template,
            materialized=True,
            columns=[
                c.Column("gid", "integer", "Autonumérico para visionado."),
                c.Column("per_cobertura", "double precision", "Porcentaje de cobertura de construcciones frente a la parcela"),
                c.Column("area_centroide", "geometry", "Centro de masas ponderado por superficie de las construcciones."),
                c.Column("p_geom", "geometry", "Geometría de la parcela."),
                c.Column("c_parsedconstru_array", "gs__tokenizer[]", "Array de los resultados de parsear el campo constru."),
                c.Column("c_total_volumen", "double precision", "Total de volumen constructivo en la parcela."),
                c.Column("c_altura_array", "integer[]", "Array con las alturas de las construcciones."),
                c.Column("c_volumen_array", "double precision[]", "Array con los volúmenes de cada construcción. Utilizado para calcular el centro de masas ponderado por volumen."),
                c.Column("volumen_centroide", "geometry", "Centro de masas ponderado por volumen."),
                c.Column("p_centroid", "geometry", "Centroide de la parcela."),
                c.Column("c_num_constru", "integer", "Número de construcciones en la parcela."),
                c.Column("c_total_area", "double precision", "Área total de las construcciones."),
                c.Column("c_individual_geoms", "geometry[]", "Array con las geometrías de las construcciones."),
                c.Column("c_geoms", "geometry", "Geometrías de las construcciones (multipolygon)."),
                c.Column("c_centroids_array", "geometry[]", "Array de los centroides de las construcciones. Utilizado para calcular el centro de masas ponderado."),
                c.Column("c_centroids", "geometry", "Centroides de las parcelas (multipoint)"),
                c.Column("c_areas_array", "double precision[]", "Array con las áreas de las construcciones. Utilizado para calcular el centro de masas ponderado.")],
            owner=role_catastro_admin,
            indexes=[("btree", "gid"), ("gist", "area_centroide"), ("gist", "volumen_centroide"),
                     ("gist", "p_geom"), ("gist", "p_centroid"), ("gist", "c_geoms"), ("gist", "c_centroids")])

views.append(mv)



# Schema

schema_procesamiento_base = c.Schema("procesamiento_base",
                                     "Procesamiento base de catastro",
                                     owner=role_catastro_admin,
                                     permissions=[(role_catastro_users.grant, "usage"),
                                                  (role_geoserver.grant, "usage")],
                                     views=views)


    


# --------------------------------------
# agregaciones_rejilla schema definition
# --------------------------------------

# Materialized view mvw__constru_en_parcelas

views = []

# Materialized view mvw__constru_par_grid_SIZE_METODO

template = c.Helpers.getSnippet("0050-agregaciones_rejilla-materialized_views.sql",
                                tag="template_c_aerea_parcelas_grid")

for m in [{"method": "volumen_centroide", "name": "centroide ponderado por volumen"},
          {"method": "area_centroide", "name": "centroide ponderado por área"},
          {"method": "p_centroid", "name": "centroide geométrico"}]:
    for i in range(0, len(gridSuffix)):
        mv = c.View("mvw__c_par_grid_%s_%s" % (gridSuffix[i], m["method"]),
                    "Asignación a la rejilla de %s metros de los indicadores de las parcelas en función de la rejilla en la que cae el %s de la parcela." % (gridSizes[i], m["name"]),
                    sql=c.Helpers.template(template, {"grid": gridSuffix[i], "method": m["method"]}),
                    materialized=True,
                    columns=[
                        c.Column("grid_gid", "integer", "Autonumérico para visionado, de la rejilla."),
                        c.Column("parcelas_media_per_cobertura", "double precision", "Media de los porcentajes de ocupación de las parcelas por vivienda para el total de la celda."),
                        c.Column("parcelas_geoms", "geometry",
                                 "Conjunto de las geometrías cuyo %s cae dentro en la celdilla." % m["name"]),
                        c.Column("parcelas_area_total", "double precision",
                                 "Área total de las parcelas cuyo %s cae dentro de la celdilla." % m["name"]),
                        c.Column("parcelas_centroids", "geometry", "Total de centroides de parcelas dentro de la celdilla."),
                        c.Column("num_construcciones", "integer",
                                 "Número de construcciones en las rejillas cuyo %s está dentro de la celdilla." % m["name"]),
                        c.Column("constru_total_area", "double precision",
                                 "Área total de las construcciones presentes en las parcelas cuyo %s está dentro de la celdilla." % m["name"]),
                        c.Column("per_cobertura_total", "double precision",
                                 "Porcentaje de cobertura total dado por la suma total del área de las construcciones incluidas en las parcelas cuyo %s está dentro de la celdilla y el área de las mismas parcelas." % m["name"]),
                        c.Column("constru_geoms", "geometry",
                                 "Conjunto de las geometrías de las construcciones presentes en parcelas cuyo %s está dentro de la rejilla." % m["name"]),
                        c.Column("constru_centroides", "geometry",
                                 "Conjunto de centroides de las construcciones presentes en parcelas cuyo %s está dentro de la rejilla." % m["name"]),
                        c.Column("constru_area_centroide", "geometry",
                                 "Conjunto de centroides ponderados de las construcciones presentes en parcelas cuyo %s está dentro de la rejilla." % m["name"]),
                        c.Column("constru_parsedconstru_array", "gs__tokenizer[]", "Array de resultados de tokenización del campo constru"),
                        c.Column("constru_total_volumen", "double precision", "Volumen total de construcciones en parcela"),
                        c.Column("grid_geom", "geometry", "Geometría de la rejilla."),
                        c.Column("constru_volumen_centroide", "geometry", "Conjunto de centros de masa ponderados por volumen en la parcela"),
                        c.Column("constru_volumen_array", "double precision[]", "Array de los volúmenes de las construcciones en la rejilla.")],
                    owner=role_catastro_admin,
                    indexes=[("btree", "grid_gid", "mvw__c_par_grid_%s_%s_gid" % (gridSuffix[i], m["method"][1])),
                             ("gist", "parcelas_geoms", "mvw__c_par_grid_%s_%s_p_geom" %
                              (gridSuffix[i], m["method"][1])),
                             ("gist", "grid_geom", "mvw__c_par_grid_%s_%s_g_geom" %
                              (gridSuffix[i], m["method"][1])),
                             ("gist", "parcelas_centroids", "mvw__c_par_grid_%s_%s_p_cent" %
                              (gridSuffix[i], m["method"][1])),
                              ("gist", "constru_geoms", "mvw__c_par_grid_%s_%s_c_geom" %
                               (gridSuffix[i], m["method"][1])),
                             ("gist", "constru_centroides", "mvw__c_par_grid_%s_%s_c_cent" %
                              (gridSuffix[i], m["method"][1])),
                             ("gist", "constru_area_centroide", "mvw__c_par_grid_%s_%s_c_a_cent" %
                              (gridSuffix[i], m["method"][1])),
                             ("gist", "constru_volumen_centroide", "mvw__c_par_grid_%s_%s_c_v_cent" %
                              (gridSuffix[i], m["method"][1]))])
    
        views.append(mv)

    
# Schema

schema_agregaciones_rejilla = c.Schema("agregaciones_rejilla",
                                       "Análisis de agregación de información sobre grids",
                                       owner=role_catastro_admin,
                                       permissions=[(role_catastro_users.grant, "usage"),
                                                    (role_geoserver.grant, "usage")],
                                       views=views)



# ----------------------
# Schema inundable_costa
# ----------------------

tables = []

# Table inundable_costa.inundable_costa

tb_inundable_costa_inundable_costa = c.Table(
    "inundable_costa",
    "Máscara de zona inundable en la costa. Un único polígono.",
    [
        c.Column("gid", "bigint", "Numérico identificador."),
        c.Column("geom", "geometry(POLYGON, 25830)",
                 "Geometría multipoligonal de la zona inundable en la costa.")],
    "gid", ("gist", "geom"), role_catastro_admin)

tables.append(tb_inundable_costa_inundable_costa)


# Analytics materialized views

views = []

views.append(
    c.View(
        "mvw__inundable_parcelas",
        "Vista materializada de todos los GID de parcelas en contacto con la zona inundable.",
        """
        select distinct
          a.gid
        from
          fase_0.catastro__c_parcelas_andalucia a inner join
          inundable_costa.inundable_costa b on st_intersects(a.geom, b.geom)
        """,
        materialized=True,
        columns=[
            c.Column("gid", "bigint", "GID de las parcelas en contacto con la zona inundable.")],
        indexes=[("btree", "gid")],
        owner=role_catastro_admin))

views.append(
    c.View(
        "mvw__inundable_constru",
        "Vista materializada de todos los GID de construcciones en contacto con la "+ \
        "zona inundable.",
        """
        select distinct
          a.gid
        from
          fase_0.catastro_normalized_import_20150330__constru a inner join
          inundable_costa.inundable_costa b on st_intersects(a.geom, b.geom)
        """,
        materialized=True,
        columns=[
            c.Column("gid", "bigint", "GID de las construcciones en contacto con la zona "+ \
                     "inundable.")],
        indexes=[("btree", "gid")],
        owner=role_catastro_admin))

views.append(
    c.View(
        "mvw__inundable_constru_alturas",
        "Vista materializada con los GID de procesamiento_base.mvw__constru que caen en la zona inundable.",
        """
        select distinct
          a.gid
        from
          procesamiento_base.mvw__constru a inner join
          inundable_costa.inundable_costa b on st_intersects(a.geom, b.geom)
        """,
        materialized=True,
        columns=[
            c.Column("gid", "bigint", "GID de procesamiento_base.mvw__constru que caen en la zona inundable.")],
        indexes=[("btree", "gid")],
        owner=role_catastro_admin))

for i in config.gridNames:
    views.append(
        c.View(
            "mvw__inundable_c_par_grid_%s_vol_cent" % i,
            "Vista materializada con los GID de agregaciones_rejilla.mvw__c_par_grid_%s_volumen_centroide que cae en la zona inundable." % i,
            """
            select distinct
              a.grid_gid as grid_gid
            from
              agregaciones_rejilla.mvw__c_par_grid_%s_volumen_centroide a inner join
              inundable_costa.inundable_costa b on st_intersects(a.grid_geom, b.geom)
            """ % i,
            materialized=True,
            columns=[
                c.Column("grid_gid", "bigint", "GID de agregaciones_rejilla.mvw__c_par_grid_%s_volumen_centroide que cae en la zona inundable." % i)],
            indexes=[("btree", "grid_gid")],
            owner=role_catastro_admin))

views.append(
    c.View(
        "vw__inundable_parcelas",
        "Vista de las parcelas en contacto con la zona inundable.",
        """
        select
          a.*
        from
          fase_0.catastro__c_parcelas_andalucia a inner join
          inundable_costa.mvw__inundable_parcelas b on a.gid=b.gid
        """,
        materialized=False,
        owner=role_catastro_admin))

views.append(
    c.View(
        "vw__inundable_constru",
        "Vista de las construcciones en contacto con la zona inundable.",
        """
        select
          a.*
        from
          procesamiento_base.mvw__constru a inner join
          inundable_costa.mvw__inundable_constru_alturas b on a.gid=b.gid
        """,
        materialized=False,
        owner=role_catastro_admin))

for i in config.gridNames:
    views.append(
        c.View(
            "vw__inundable_c_par_grid_%s_volumen_centroide" %i,
            "Vista de las celdas de agregaciones_rejilla.mvw__c_par_grid_%s_volumen_centroide que caen en la zona inundable." % i,
            """
            select
              a.*
            from
              agregaciones_rejilla.mvw__c_par_grid_%s_volumen_centroide a inner join
              inundable_costa.mvw__inundable_c_par_grid_%s_vol_cent b on a.grid_gid=b.grid_gid
            """ % (i,i),
            materialized=False,
            owner=role_catastro_admin))
    

# Schema

schema_inundable_costa = c.Schema(
    "inundable_costa",
    "Análisis de efectos de inundabilidad.",
    owner=role_catastro_admin,
    permissions=[(role_catastro_users.grant, "usage"),
                 (role_geoserver.grant, "usage")],
    tables=tables,
    views=views)
                 


# ----------------
# Schema test_data
# ----------------

schema_test_data = c.Schema("test_data", "Esquema para la extracción de datos de prueba",
                            owner=role_catastro_admin)
