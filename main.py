"""
This file contains my interpretation of the requested sample scripts
requested for the `ourkettle.com` tech assessment.
"""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
import geopandas as gpd
import fsspec
import numpy as np
from shapely import wkt
from tqdm import tqdm

def get_query_engine(
        conn_str:str="postgresql://postgres:password@localhost:5432/postgres"
) -> Engine:
    """
    Create a sqlalchemy engine to connect to a database

    Args:
        conn_str: sqlalchemy supported connection string

    Returns:
        The sqlalchemy connection engine

    """

    return create_engine(conn_str)


def validate_geometry(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Validate the geometries in a dataframe

    Args:
        df: The dataframe to be sanitized of invalid geometries

    Returns:
        A dataframe with any rows removed that contain invalid geometries
    """
    return df[df['geometry'].is_valid]


def store_data(df: gpd.GeoDataFrame,
               table_name:str = 'parcels',
               schema_name:str='public',
               mode:str='append',
               chunk_size:int=500,
               validate:bool=True) -> None:
    """
    Write parcel data to a postgis database

    Args:
        df: dataframe containing geospatial data to put into the database
        table_name: name of the table to insert the data into
        schema_name: name of the schema where the table resides
        mode: mode in which to use when writing data
        chunk_size: number of rows to insert at a time
        validate: validate the geometry

    Returns:
        None
    """

    engine = get_query_engine()

    for chunk in tqdm(np.array_split(df, chunk_size), desc="Uploading..."):
        if validate:
            chunk = validate_geometry(chunk)
        # convert to 4326 to keep the geometries in a format for easy viz/interaction
        chunk = chunk.to_crs('EPSG:4326')
        chunk.to_postgis(
            table_name,
            engine,
            if_exists=mode,
            schema=schema_name,
            chunksize=chunk_size
        )


def area_of_random_parcels(num_samples: int=5):

    """
    Calculate the total area of a random sample of parcels
    in a database

    Args:
        num_samples: number of samples to take from the database with
        which to calculate a total area

    Returns:
        Total area in square meters

    """
    engine = get_query_engine()
    query = f"""SELECT SUM(a.area) as total_area
    FROM (
        SELECT ST_AREA(ST_TRANSFORM(geometry, 3857)) AS "area" 
        FROM parcels
        OFFSET FLOOR(RANDOM() * (SELECT COUNT(*) FROM parcels))
    LIMIT {num_samples}) AS a;
    """
    return engine.execute(query).one()[0]


def get_parcels_in_aoi_geojson(file_name:str,
                               table_name:str='parcels'):
    """
    Get the number of parcels that intersect with an area of interest
    Args:
        file_name: the geojson file containing the area of interest
        table_name: the name of the table to check geometry intersection on

    Returns:
        The number of parcels that intersect with the area of interest
    """
    engine = get_query_engine()
    aoi_ds = gpd.read_file(file_name)
    aoi_geom_string = wkt.dumps(aoi_ds['geometry'][0])
    aoi_query_string = f"""
     select count(*)
        from {table_name}
        where st_intersects(
        geometry,
            'SRID=4326;{aoi_geom_string}'
        )
    """
    return engine.execute(aoi_query_string).one()[0]


if __name__ == '__main__':

    # read in the data
    print("Reading parcel data...")

    zip_file = 'data/parcels_public.zip'
    with fsspec.open(zip_file) as file:
        df = gpd.read_file(file, layer='parcels_public')

    print(f"{df.shape[0]:,} rows of parcel data ingested.")

    # insert the data into the database
    print("Putting parcel data into the database...")

    store_data(df)

    print("Parcel data inserted into the database!")

    # perform some analytical operations
    number_of_parcels = 3
    aoi_geojson = 'data/aoi.geojson'

    print(
        "Performing an analytic operations to calculate..."
    )
    print(f"The total area of {number_of_parcels} random parcels is: "
          f"{area_of_random_parcels(num_samples=number_of_parcels):,} square meters"
          )
    print(
        f'There are {get_parcels_in_aoi_geojson(aoi_geojson)} parcels in the area of interest!'
    )

    print('Done!')
