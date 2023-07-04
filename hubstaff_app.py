
import sys
import datetime
from collections import defaultdict
from operator import itemgetter
from typing import Literal
from tabulate import tabulate
from utils import logger, get_config
from hubstaff import HubstaffClient

HTML_HEADER = """<!DOCTYPE html>
<html>
<head>
    <title>Time logged</title>
    <link rel="stylesheet"
        href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css"
        crossorigin="anonymous">
</head>
<body>
"""

HTML_FOOTER = """
</body>
</html>
"""

def draw_html_table(rows: list[list[str]], header: list[str], colalign: list[str], extended=True) -> str:
    """
        Draw the table in HTML format, adding some styles from Bootstrap. These styles won't work in email.

        Parameters:
        rows: list of table rows, each row contains a cell value
        header: list of column headers
        colalign: list of column alignments. See help for [tabulate lib](https://github.com/astanin/python-tabulate)
        extended: if True - the complete HTML document returned, otherwise only table (to include in other docs)

        Returns:
        str: HTML text with the table

    """
    table = tabulate(rows, headers=header, tablefmt='html', colalign=colalign)
    table = table.replace('<table>', '<table class="table table-sm table-bordered">')
    if extended:
        divstart = '<div class="row"><div class="col-12">'
        divend = '</div></div>'
        return HTML_HEADER + divstart + table + divend + HTML_FOOTER
    return table


def draw_table(rows: list[list[str]], header: list[str], colalign: list[str],
               table_format: Literal['ascii', 'html'] = 'html') -> str:
    """
        Draw the table in one of supported formats.

        Parameters:
        rows: list of table rows, each row contains a cell value
        header: list of column headers
        colalign: list of column alignments. See help for [tabulate lib](https://github.com/astanin/python-tabulate)
        table_format: format name. Supported formats are: [ascii, html]
    """
    table = ''
    if not rows:
        return ''

    if table_format == 'html':
        table = draw_html_table(rows, header=header, colalign=colalign)
    elif table_format == 'ascii':
        # for the debug purposes we may want to output the table to the console
        table = tabulate(rows, headers=header, tablefmt='presto', colalign=colalign)
    else:
        raise NotImplementedError(f"Format {table_format} is not supported")
    return table


def main(args: list[str]) -> int:
    try:
        config = get_config(args)
        organization_id = config.get('organization_id')
        start_date = config['start_date']
        with HubstaffClient(
                api_base_url=config['hubstaff'].get('api_base'),
                email=config['hubstaff']['email'],
                password=config['hubstaff']['password'],
                token=config['hubstaff']['token'],
                logger=logger,
            ) as hclient:

            if not organization_id:
                organizations = hclient.get_organizations()
                if len(organizations) == 1:
                    organization_id = organizations[0]['id']
                    logger.debug(f"Using organization #{organizations[0]['name']}: {organizations[0]['name']}")
                else:
                    raise Exception(
                        f"Cannot pick one organization within {len(organizations)}. Set organization_id in settings")

            # there is an API method that could return all data at once
            response = hclient.get_organization_activities_daily(organization_id,
                                                                 start_date, include=['users', 'projects'])

        # users and projects will be displayed ordered by names
        users = sorted(response['users'], key=itemgetter('name'))
        projects = sorted(response['projects'], key=itemgetter('name'))

        # aggregate tracked time
        proj2member_activity = defaultdict(lambda: defaultdict(int))
        for activity in response['daily_activities']:
            proj2member_activity[activity['project_id']][activity['user_id']] += activity['tracked']

        # preparing the table
        header = ['']
        rows = []
        colalign = ['right', ]  # alignment for the cells
        for user in users:
            header.append(user['name'])
            colalign.append('center')
        for project in projects:
            row = [project['name']]
            for user in users:
                if value := proj2member_activity[project['id']][user['id']]:
                    row.append(str(datetime.timedelta(seconds=value)))
                else:
                    row.append(None)
            rows.append(row)

        table = draw_table(rows, header, colalign, table_format=config['format'])
        if table:
            print(table)
        else:
            print("  No data for the given date")

        return 0
    except SystemExit:  # argparser exits forcefully after a parsing error or helps
        return -1
    except:
        logger.exception("Error")
        return 1


if __name__ == '__main__':
    retval = main(sys.argv[1:]) or 0
    sys.exit(retval)
