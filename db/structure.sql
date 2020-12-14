drop table if exists source_filenames;
create table source_filenames
( id serial primary key
, filename text not null
);
create unique index unique_source_filenames on source_filenames(filename);

drop table if exists factors;
create table factors
( id serial primary key
, source_filename_id integer not null
, occurred_at date not null
, mkt_rf numeric not null
, smb numeric not null
, hml numeric not null
, rf numeric not null
, mom numeric
, rmw numeric
, cma numeric
);

alter table factors
add constraint fk_factors_source_filename_id
foreign key (source_filename_id)
references source_filenames (id)
deferrable initially deferred;


drop table if exists ticker_prices;
create table ticker_prices
( id serial primary key
, symbol text not null
, occurred_at date not null
, percentage_change numeric not null
);

create unique index uniqify_ticker_prices_by_occurrence ON ticker_prices (symbol, occurred_at);
