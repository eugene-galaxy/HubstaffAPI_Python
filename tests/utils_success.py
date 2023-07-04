
"""
    This module contains common constants and functions to initialize successful tests
"""

from pytest_httpx import HTTPXMock

BASE_API = 'http://base_api'
APPTOKEN = 'testtest'
AUTHTOKEN = 'secret'
DATE_START = '2023-06-06'
ORGANIZATION_ID = 123
ORGANIZATION = {'id': ORGANIZATION_ID, 'name': 'Test organization'}
USERS = [
    {'id': 33, 'name': 'User 33'},
    {'id': 44, 'name': 'User 44'},
    {'id': 55, 'name': 'User 55'},
]
PROJECTS = [
    {'id': 777, 'name': 'Project 777'},
    {'id': 888, 'name': 'Project 888'},
    {'id': 999, 'name': 'Project 999'},
]
ACTIVITIES = [
    {
        "id": 10,
        "date": DATE_START,
        "user_id": USERS[0]['id'],
        "project_id": PROJECTS[0]['id'],
        "tracked": 1800,
    },
    {
        "id": 20,
        "date": DATE_START,
        "user_id": USERS[1]['id'],
        "project_id": PROJECTS[0]['id'],
        "tracked": 2700,
    },
    {
        "id": 30,
        "date": DATE_START,
        "user_id": USERS[2]['id'],
        "project_id": PROJECTS[1]['id'],
        "tracked": 2700,
    },
    {
        "id": 30,
        "date": DATE_START,
        "user_id": USERS[0]['id'],
        "project_id": PROJECTS[2]['id'],
        "tracked": 2700,
    },
]


def prepare_mocks(httpx_mock: HTTPXMock):
    " Prepare predefined answers for the successful tests "
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE_API}/user/auth?app_token={APPTOKEN}",
        json={'auth_token': AUTHTOKEN},
        status_code=200,
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE_API}/companies?app_token={APPTOKEN}",
        json={'organizations': [ORGANIZATION]},
        status_code=200,
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE_API}/companies/{ORGANIZATION_ID}/operations/day"
            f"?date%5Bstart%5D={DATE_START}&date%5Bstop%5D={DATE_START}&include=users%2Cprojects&app_token={APPTOKEN}",
        json={'daily_activities': ACTIVITIES, 'users': USERS, 'projects': PROJECTS},
        status_code=200,
    )
