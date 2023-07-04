
import sys
import os
import argparse
import datetime
from pathlib import Path

os.environ['LOGURU_AUTOINIT'] = 'false'
from loguru import logger, _defaults as lgdefaults
import yaml

# init logger, with default settings
logger.add(sys.stderr, level='INFO', format=lgdefaults.LOGURU_FORMAT)


def parse_args(arguments):
    " Parse command-line arguments "
    parser = argparse.ArgumentParser(description="Fetch employees time from Hubstaff",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,)
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable debug output')
    parser.add_argument('-c', '--config', help='Config file', required=False)
    parser.add_argument('-o', '--organization', help='Organization ID', type=int, required=False)
    parser.add_argument('-d', '--date', help='Date (YYYY-MM-DD) or date offset in days (1, 2, 3, ...)', required=False)
    parser.add_argument('--format', choices=['html', 'ascii'], help='Table format. Default is html', required=False)

    parsed_args = parser.parse_args(arguments)
    return parsed_args


def setup_logger(loglevel: str | int = 'INFO') -> None:
    """
        Set logger's log level.
        As soon as the script's results should be output to the stdout, we can use only stderr for the log records
    """
    logger.remove()
    logger.add(sys.stderr, level=loglevel, format=lgdefaults.LOGURU_FORMAT)


def get_config(arguments: list[str]) -> dict:
    """
        Prepare the settings for the application, merge settings from various sources.
        Sources in the order of precedence (the latter overwrites previious):
        - defaults (hardcoded)
        - config file
        - command-line arguments

        Been ran with the command-line argument `--help` the help will be displayed.

        Parameters:
        arguments: list of command-line arguments to parse.

    """
    config = {}
    loglevel = 'INFO'
    settings_file = Path('settings.yaml')
    args = None
    if arguments:
        args = parse_args(arguments)

    if args and args.config:
        settings_file = Path(args.config)
    # NOTE: it is possible to implement extended config validation with Pydantic,
    # but it will be an overkill for such small script.
    # Any erroneous value will cause an error later anyway
    config = yaml.safe_load(settings_file.read_text())

    if args and args.verbose:
        loglevel = 'DEBUG'

    if args and args.organization:
        config['organization_id'] = args.organization

    # Date can be specified as a date string (YYYY-MM-DD) as an integer offset (always counted back) to the current date
    start_date = datetime.date.today() - datetime.timedelta(days=1)
    sdate = config.get('date') or '1'
    if args and args.date:
        sdate = args.date
    if sdate.isnumeric() or sdate.startswith('-') and sdate[1:].isnumeric():
        start_date = datetime.date.today() - datetime.timedelta(days=abs(int(sdate)))
    else:
        start_date = datetime.datetime.strptime(sdate, '%Y-%m-%d').date()
    config['start_date'] = start_date

    if args and args.format:
        config['format'] = args.format
    else:
        config['format'] = config.get('format') or 'html'

    loglevel = config.get('loglevel') or loglevel
    setup_logger(loglevel=loglevel)

    return config
