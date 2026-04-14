--
-- PostgreSQL database cluster dump
--

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Roles
--

CREATE ROLE npd_readonly_db_user;
ALTER ROLE npd_readonly_db_user WITH NOSUPERUSER INHERIT NOCREATEROLE NOCREATEDB LOGIN NOREPLICATION NOBYPASSRLS PASSWORD 'SCRAM-SHA-256$4096:55LGzvIuKyJpRYXO0vFe/w==$wPiFxDHQz72NqtPJHdnqFrfOMc57x33nEcmyUv0Dwe4=:oWUUF88Mchok8kJVYH1rhx/SUTQur6CNwNaiTkWdU6A=';
CREATE ROLE postgres;
ALTER ROLE postgres WITH SUPERUSER INHERIT CREATEROLE CREATEDB LOGIN REPLICATION BYPASSRLS PASSWORD 'SCRAM-SHA-256$4096:sSDSYtpTqCzkSm9EP88bMg==$wD2pE4I8ey7bFXomeNJDJ8srOqbJNY9w29Ybt+/6kmg=:tYev6PS14jJAvohwXPiPf+YW1Gbq15aGNAv5xgpFdO8=';

--
-- User Configurations
--


--
-- Role memberships
--

GRANT pg_read_all_data TO npd_readonly_db_user WITH INHERIT TRUE GRANTED BY postgres;






--
-- PostgreSQL database cluster dump complete
--

