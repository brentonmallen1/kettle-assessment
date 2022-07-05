# Kettle Assessment

Author: Brenton Mallen


## Request 1: System Design
- See iPad [sketch file](system-design-sketch.jpeg) for a simple visualization

The system design would depend on a lot of parameters (including data ingestion rates, types of analytic processes, etc.), but a generic design would contain some version of the following:

- Ingestion
  - A means to ingest data of a given format
    - Translators that make the ingestion black box to convert files
    like `shp` to the database schema
  - If ingestion is a streaming process, some means to be aware of new data
  becoming available (i.e. SQS/CloudEvent) and put onto a job queue
    - Database should have an ID that is a hash of attributes of each item
    in the database to ensure idempotency in case data needs to
    be reingested/replayed

- Database
  - Database of choice would be PostGIS
    - This would allow for geospatial functionality on top of a common and easy to use/integrate database, PostgreSQL.
    - This allows for making queries at scale for things like geometry overlaps, area calculations, etc.

- Analytic Functionality
  - Ad Hoc
    - Queries can be made directly to the database
    - An RESTful API interface could be put in front of the database if there's
    a need for that
  - Long Running / Batch Jobs
    - This could be done in something like Apache Airflow or AWS Batch/Lambda
    depending on the computation power needed
      - These tools allow for things like scheduling, monitoring, alerting, and
      re-processing (idempotency can be important here) 
    - Output of the jobs could be put into a static location like S3 or
    put into a database that can then be used to feed a dashboard in something
    like Streamlit

## Request 2: Scripts

### Schema for Storage
An example schema for the data storage can be found in the `init.sql` file.

This file is used for initializing the [database](#database).

### Running the Script

#### Environment
- This project was developed using a [conda](https://docs.conda.io/en/latest/miniconda.html) environment
  - the `environment.yml` file contains the environment description
    - Build the environment using `conda env update` from the project's root directory
    - Once the environment has been built, it can be activated by running `conda activate kettle`

#### Database
- The script in this project relies on a PostGIS database which can be created by running `make database`
  - This will perform the following actions:
    1. Spin up a PostGIS database in a container
    2. Create a table with a schema 
    3. Expose the `5432` port so that a connection to the database can be made

**Note:** To check that the database container is running,
execute `docker ps` and the container should be there.

### Running the Scripts

**Procedure:**
1) Activate the [conda environment](#environment)
2) Spin up the [database](#database)
3) Run the script by executing `python main.py` in the project's root directory


### Cleanup
- Run `make teardown` to clean up the database container when cleaning down. 
- Ensure the container has been terminated by executing `docker ps` and verifying that the container is not present
