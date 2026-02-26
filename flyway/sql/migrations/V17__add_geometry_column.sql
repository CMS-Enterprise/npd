create extension postgis;

alter table ${apiSchema}.address_us add column geolocation geometry;
alter table ${apiSchema}.address_international add column geolocation geometry;
alter table ${apiSchema}.address_nonstandard add column geolocation geometry;

update ${apiSchema}.address_us set geolocation = ST_point(longitude, latitude);
update ${apiSchema}.address_international set geolocation = ST_point(longitude, latitude);
update ${apiSchema}.address_nonstandard set geolocation = ST_point(longitude, latitude);