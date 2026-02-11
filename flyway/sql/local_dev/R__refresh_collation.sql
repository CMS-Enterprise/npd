-- resolves collation version mismatch when docker's base image OS is the incorrect version

ALTER DATABASE postgres REFRESH COLLATION VERSION;
ALTER DATABASE template1 REFRESH COLLATION VERSION;
ALTER DATABASE ${NPD_DB_NAME} REFRESH COLLATION VERSION;