drop table if exists stock_markets;
create table source_filenames
( id serial primary key
, filename text
);
create unique index unique_source_filenames on source_filenames(filename);

drop table if exists factors;
create table factors
( id serial primary key
, source_filename_id integer not null
, mkt_rf numeric not null
, smb numeric not null
, hml numeric not null
, rf numeric not null
, mom numeric
, rmw numeric
, cma numeric
);
