drop table if exists market_types;

create table market_types
( id serial primary key
, name text not null
);

create unique index market_type_names on market_types(name);

drop table if exists factor_returns;

create table factor_returns
( id serial primary key
, market_type_id integer not null
, occurred_at date not null
, risk_free numeric not null
, market_minus_risk_free numeric not null
, small_minus_big numeric not null
, high_minus_low numeric not null
, robust_minus_weak numeric not null
, conservative_minus_aggressive numeric not null
, winners_minus_losers numeric not null
);

create unique index uniqify_factor_returns_by_occurrence ON factor_returns (market_type_id, occurred_at);

alter table factor_returns
add constraint fk_factor_returns_market_type_id
foreign key (market_type_id)
references market_types (id)
deferrable initially deferred;


drop table if exists ticker_prices;
create table ticker_prices
( id serial primary key
, symbol text not null
, occurred_at date not null
, percentage_change numeric not null
);

create unique index uniqify_ticker_prices_by_occurrence ON ticker_prices (symbol, occurred_at);
