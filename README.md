# Data connector
The Data Connector app processes a CSV file containing customer records and sends the data to an external API. This project was developed as part of a home assignment by Meiro. The app features a REST API for seamless integration into your infrastructure, and it also includes a simple CLI for manual data operations.

Please note that the app was developed on a Linux system, so certain commands for manual installation may not be compatible with Windows. On Windows, use `py` instead of `python`.


## Requirements
To run the app, you'll need the following technologies:
- Python 3.9+,
- [docker](https://www.docker.com/),
- poetry (optional, recommended for developers).

## Installation
Clone the repository and navigate to the project directory:
```bash
git clone https://github.com/hungdojan/DataConnectorMeiro
cd DataConnectorMeiro
```

### Build a Docker image
To build a Docker container image, use the following commands:
```sh
# Build the Docker image
docker build -t data-connector .

# Verify the image creation
docker images
```
You should see an image named data-connector in the output.

### Install dependencies using pip (or poetry)
You have two options for installing dependencies: via pip or poetry.

##### Using Pip
```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install the required dependencies
pip install -r requirements.txt
```

##### Using Poetry
```bash
# Install the dependencies with poetry
poetry install

# To include testing dependencies
poetry install --with test
```

## Configuration
Before running the app, make sure to set the following environment variables:

- `API_URL` - The URL of the external API to send processed data to.
- `PROJECT_KEY` - The project key value.
- `MIN_AGE` (optional) - Minimum age for filtering (default: 18). Numerical value is expected.
- `MAX_AGE` (optional) - Maximum age for filtering (default: no limit). Numerical value is expected.
- `FAILED_RECORDS_DIRPATH` (optional) - Directory for storing failed records (default: `/recover_dir` inside the container, `/tmp` on the host).
- `LOGLEVEL` (optional) - Set the logging level. Supported values are `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL` (default: `WARNING`).

### Running the App
##### Using Docker
You can run the app in a Docker container with the following command:
```bash
docker run -p 5000:5000 \
    -e API_URL=<external-api-url> \
    -e PROJECT_KEY=<project-key> \
    -v <dir-on-host>:/recover_dir \
    data-connector:latest
```

Example or running the container:
```bash
docker run -p 5000:5000 \
    -e API_URL="http://testapi.com" \
    -e PROJECT_KEY="project-key" \
    -e MIN_AGE="21" \
    -v /tmp:/recover_dir \
    data-connector:latest
```
##### Running locally
To run the app locally, you can use [Gunicorn](https://docs.gunicorn.org/en/latest/run.html#) or [Flask's CLI](https://flask.palletsprojects.com/en/stable/quickstart/#a-minimal-application).

```bash
gunicorn -b 0.0.0.0:5000 --chdir src wsgi:app
```

### Docker compose Integration
To include the Data Connector in your existing infrastructure using Docker Compose, add it as a service in your `docker-compose.yml`:

```yaml
services:
    data-connector:
        build: ./DataConnectorMeiro
        environment:
            # check the list of environment variables above
            API_URL: <external-api-url>
            PROJECT: <project-key>
        # set networks if necessary
        networks:
            - ...
        ports:
            - 5000:5000
        # mount recover directory
        volumes:
            - <dir-on-host>:/recover_dir
    ...
```

The app will run on port 5000 by default. Access it at `http://localhost:5000` or `data-connector:5000` within the Docker network.


## REST API documentation
The app exposes several endpoints for interacting with the data. Access the Swagger UI documentation at `http://localhost:5000` once the app is running.

#### Send a single record
```
Endpoint: /send_record
Request body: {
    name: <customer-name>,
    age: <customer-age>,
    cookie: <customer-cookie>.
    banner_id: <customer-banner-id>,
    max_age (optional): <max-age-filter>,
    min_age (optional): <min-age-filter>,
}
Possible responses:
    202, { message: <task-output-message>},
    400, { message: <fail-message> }
```

#### Upload a CSV file
```
Endpoint: /send_record/bulk
Form parameters: {
    file: <file-data>,
    max_age (optional): <max-age-filter>,
    min_age (optional): <min-age-filter>,
}
Possible responses:
    202: { sent: <number-of-sent-records> },
    400: { message: <error-while-sending-file> },
    415: { message: <unsupported-file-type> }
```

Example of file upload using cURL command with the `MAX_AGE` filter:
```sh
curl -X 'POST' \
  'http://localhost:5000/send_record/bulk' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@data.csv;type=text/csv' \
  -F 'max_age=30'
```

## CLI command usage
The app includes a CLI command to manually upload a CSV file. The command is available inside the container.

#### upload-file
To use the `upload-file` command:

```
$ flask upload-file --help
Usage: flask upload-file [OPTIONS] FILENAME

  CLI command to process CSV file.

  :param str filename: File path to the CSV file.

Options:
  -mi, --minimum INTEGER  Minimum age filter
  -ma, --maximum INTEGER  Maximum age filter
  --help                  Show this message and exit.
```
