FROM postgis/postgis:14-3.2
ADD ./init.sql /docker-entrypoint-initdb.d/
