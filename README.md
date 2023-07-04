

# Hubstaff: Employees' Logged Time

The script is intended to pull the time logged in a day by the employees of the organization from the Hubstaff API (its test substitute). Results will be displayed in the table form and output will be made to stdout.

## Setup

Make sure that Docker is installed on your server.

Create file `settings.yaml` (see file `settings_example.yaml`). Put your credentials to the file accordingly.

Run the script to build the image and the container. You can add command-line arguments to the script to be added to the script on run. See the list of arguments in the next section.

    sudo bash build.sh -v

Parameter `-v` will output additional log records to the stderr output. `sudo` is required on Linux-based platforms as by default docker can be ran from superusers.

## Run

You can just start the docker container (attached to the console) to grab the output.

    sudo docker start -a hubstafftimelog > logged_time.html

## Usage and Command-line Parameters

```
usage: hubstaff_app.py [-h] [-v] [-c CONFIG] [-o ORGANIZATION] [-d DATE] [--format {html,ascii}]

Fetch employees time from Hubstaff

options:
  -h, --help            show this help message and exit
  -v, --verbose           Enable debug output
  -c CONFIG, --config CONFIG
                        Config file
  -o ORGANIZATION, --organization ORGANIZATION
                        Organization ID
  -d DATE, --date DATE  Date (YYYY-MM-DD) or date offset in days (1, 2, 3, ...)
  --format {html,ascii}
                        Table format. Default is html
```

* organization - if there is only one organization available for the API user - it will be used by default.

* date - by default value `-1` is used, meaning "yesterday"


## Testing

Run pytest:

    pytest

