    
# # ---------
# # Databases
# # ---------

# db_postgres = c.Database(conf["superdb"], conf["host"], conf["port"], "The super DB.")

# db_catastro = c.Database(conf["db"], conf["host"], conf["port"],
#                          "Base de datos principal de análisis de catastro.",
#                          c.roles["catastro_admin"],
#                          [(c.roles["PUBLIC"].revoke, ["connect", "temp"]),
#                           (c.roles["catastro_users"].grant, ["connect", "temp"]),
#                           (c.roles["geoserver"].grant, ["connect"])],
#                          c.Extension("postgis"),
#                          tablespace=tablespace)

# # -------------
# # Schema public
# # -------------                          

# schema_public = c.Schema("public", "Esquema público estándar. Contiene el esquema de la extensión PostGIS.")

# tb_public_spatial_ref_sys = c.Table("spatial_ref_sys",
#                                     "Tabla estándar PostGIS para almacenamiento de información de SRS.")

# vw_public_geometry_columns = c.View("geometry_columns",
#                                     "Vista estándar PostGIS para consulta de columnas geométricas.")

# vw_public_geography_columns = c.View("geography_columns",
#                                      "Vista estándar PostGIS para consulta de columnas geográficas.")

# vw_public_raster_columns = c.View("raster_columns",
#                                   "Vista estándar PostGIS para la consulta de columnas ráster.")

# vw_public_raster_overviews = c.View("raster_overviews",
#                                     "Vista estándar PostGIS para almacenar pirámides ráster.")




# --------------
# Schema context
# --------------

# Grids tables and materialized views

# grids = [
#     {"gridSuffix": "250", "gridSize

# gridSuffix = ["250", "125", "62_5", "31_25"]
# gridSizes = [250, 125, 62.5, 31.25]

# gridTables = []
# centroidMViews = []

# for i in range(0, len(gridSuffix)):
#     gridTables.append(
#         c.Table(
#             "grid_%s" % gridSuffix[i],
#             "Rejilla de %s metros para Andalucía. Los códigos son heredados de la rejilla de referencia utilizada para su construcción, la de 250 metros del IECA (Instituto de Estadística y Cartografía de Andalucía), que a su vez se crea a partir de la rejilla oficial europea de 1 km." % gridSizes[i],
#             [
#                 c.Column("gid", "bigint", "ID de la rejilla."),
#                 c.Column("grd_fixid", "varchar(27)", "Un código de la rejilla."),
#                 c.Column("grd_floaid", "varchar(23)", "Otro código de la rejilla."),
#                 c.Column("grd_inspir", "varchar(19)", "Otro código de la rejilla."),
#                 c.Column("geom", "geometry(POLYGON, 25830)", "Geometría de la rejilla, POLYGON, EPSG 25830.")
#             ],
#             "gid", ("gist", "geom"), role_catastro_admin))
