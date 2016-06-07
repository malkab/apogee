-- Municipios test

-- -#-{municipios}

create table test_data.municipio as
select * from context.municipio
where cod_mun in ({{test_municipios}});

-- -#-{municipios}



-- Extracción de rejillas

-- -#-{rejillas}

create table test_data.grid_250 as
select
  a.*
from
  context.grid_250 a inner join
  test_data.municipio b on st_intersects(a.geom, b.geom);


create table test_data.grid_125 as
select
  a.*
from
  context.grid_125 a inner join
  test_data.municipio b on st_intersects(a.geom, b.geom);


create table test_data.grid_62_5 as
select
  a.*
from
  context.grid_62_5 a inner join
  test_data.municipio b on st_intersects(a.geom, b.geom);


create table test_data.grid_31_25 as
select
  a.*
from
  context.grid_31_25 a inner join
  test_data.municipio b on st_intersects(a.geom, b.geom);

-- -#-{rejillas}
