CREATE TABLE IF NOT EXISTS parcels (
    "ASMT" CHAR(50),
    "ASMTWithDa" CHAR(15),
    "Acres" DOUBLE PRECISION,
    "LandUse1" CHAR(4),
    "TRA" CHAR(6),
    "floor" INT,
    "Notes" CHAR(255),
    "Shape_STAr" DOUBLE PRECISION,
    "Shape_STLe" DOUBLE precision,
    "geometry" geometry(geometryz, 4326)
);