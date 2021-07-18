DROP USER IF EXISTS filecloud;
CREATE USER filecloud;
CREATE DATABASE filecloud_s3;
GRANT ALL PRIVILEGES ON DATABASE filecloud_s3 TO filecloud;