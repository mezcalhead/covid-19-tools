CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE timeseries (
	id			integer NOT NULL,
	key			varchar(180) NOT NULL,
	date		date,
	fips		char(5) NOT NULL,
	adm3		varchar(60) NOT NULL,
	adm2		varchar(60) NOT NULL,
	adm1		varchar(60) NOT NULL,
	lat			NUMERIC(9, 6),
	lon			NUMERIC(9, 6),
	geom		GEOMETRY(POINT, 4326),
	confirmed	integer NOT NULL,
	deaths		integer NOT NULL,
	recovered	integer NOT NULL,
	CONSTRAINT fkey PRIMARY KEY(key, date)
);

CREATE INDEX date_idx ON timeseries (date);
CREATE INDEX fips_idx ON timeseries (fips);
CREATE INDEX key_idx ON timeseries (key);
CREATE INDEX confirmed_idx ON timeseries (confirmed);
CREATE INDEX deaths_idx ON timeseries (deaths);
CREATE INDEX geom_idx ON timeseries USING GIST(geom);
