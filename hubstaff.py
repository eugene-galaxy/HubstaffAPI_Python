
import logging
import datetime
from typing import Literal
import httpx

BASE_URL = 'https://mutator.reef.pl/v202'
NUM_ATTEMPTS = 5
MAX_PAGES = 200
PAGE_LIMIT = 100  # default in the Hubstaff API

class HttpClientError(Exception):
    pass

class HubstaffClient:
    def __init__(self,
                 email: str,
                 password: str,
                 token: str,
                 api_base_url: str = None,
                 logger: logging.Logger = None):
        """
            Parameters:
            email: email address to log in to the API
            password: API password
            token: App token for the API
            api_base_url: URL of the root of the API
            logger: optional custom logger. If not specified - standard Python's logger is used.
        """
        self.api_base_url = api_base_url or BASE_URL
        self.email = email
        self.password = password
        self.apptoken = token
        self._auth_token = None
        self._client = None
        self.logger = logger or logging.getLogger(__name__)

    def close(self):
        " Close internal resources. "
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def _ensure_http_client(self):
        " Create HTTP transport if not yet done "
        if not self._client:
            self._client = httpx.Client(follow_redirects=True)

    def _obtain_auth_token(self):
        """ Receive auth token for the session.
            Neither app token nor auth token are likely to expire, so no need to store them permanently.
        """
        self.logger.debug("Obtaining auth token")
        params = {
            'app_token': self.apptoken,
        }
        data = {
            'email': self.email,
            'password': self.password,
        }
        url = f"{self.api_base_url}/user/auth"
        resp = self._raw_request(self._client, method='POST', url=url, params=params, data=data)
        tokendata = resp.json()
        self._auth_token = tokendata['auth_token']

    def _raw_request(self, client: httpx.Client, **kwargs):
        """
            Performs request to the given API URL.
            In case of HTTP error other than client error (4xx) it makes 5 retries.
        """
        result = None
        for attempt in range(1, NUM_ATTEMPTS + 1):
            try:
                resp = client.request(**kwargs)
                if resp.status_code == httpx.codes.OK:
                    result = resp
                    break
                if resp.status_code == httpx.codes.TOO_MANY_REQUESTS:
                    self.logger.error(f"Rate limit reached")
                    raise HttpClientError(f"Rate limit reached")
                elif httpx.codes.is_client_error(resp.status_code):
                    raise HttpClientError(f"Client error {resp.status_code}: {resp.text}")
                self.logger.error(f"Attempt {attempt}/{NUM_ATTEMPTS}: HTTP Error {resp.status_code}: {resp.text[:200]}")
            except HttpClientError:
                raise
        else:
            raise Exception(f"Cannot complete request in {NUM_ATTEMPTS} attempts")
        return result

    def _send_request(self,
                      method: Literal['GET', 'POST', 'PATCH', 'PUT', 'DELETE'], url: str,
                      params: dict = None, data: dict = None,
                      list_keys: list[str] = None) -> dict:
        """
            Prepare and send series of requests to the API.
            This method is responsible for adding authentication parameters and handling pagination.
            As soon as paginated content may be returned with several lists in one response,
            we pass parameter `list_keys` to properly extract needed parts.
            If the response is longer than 200 pages - only first 200 pages of data is returned.

            Parameters:
            method: HTTP method to use - one of: GET, POST, PUT, PATCH, DELETE.
            params: optional parameters to be passed in URL query.
            data: optional parameters to be sent in form data for POST/PUT/PATCH requests.
            list_keys: names of the items in the root of the response to be extracted in case of multi-page data
        """
        self._ensure_http_client()
        if not self._auth_token:
            self._obtain_auth_token()
        if list_keys:
            if not isinstance(list_keys, (list, set, tuple)):
                list_keys = [list_keys]
        content = None
        full_url = f"{self.api_base_url}/{url}"
        self.logger.debug(f"Sending {method} request to {url}")
        params = params or {}
        params.update({
            'app_token': self.apptoken,
        })
        headers = {
            'Accept': 'application/json',
            'AuthToken': self._auth_token,
        }

        for page in range(1, MAX_PAGES + 1):
            resp = self._raw_request(self._client, method=method, url=full_url,
                                     params=params, headers=headers, data=data)
            page_data = resp.json()
            if list_keys:
                if not content:
                    content = dict((k, []) for k in list_keys)
                for key in list_keys:
                    if key_data := page_data.get(key):
                        content[key].extend(key_data)

                if len(page_data[list_keys[0]]) < PAGE_LIMIT:
                    break
                if 'pagination' in page_data:
                    params['page_start_id'] = page_data['pagination']['next_page_start_id']
                else:
                    break

            else:
                content = page_data
                break

        else:
            self.logger.error("Reached max page {page}")

        return content

    # ------

    def get_organizations(self) -> list[dict]:
        " Retrieve organizations "
        data = self._send_request('GET', 'companies', list_keys=['organizations'])
        return data['organizations']

    def get_organization_activities_daily(self,
                                          organization_id: int,
                                          start_date: datetime.date,
                                          end_date: datetime.date | None = None,
                                          include: list['users', 'projects'] = None) -> dict[list]:
        """ Retrieve daily activities for an organization.
        It is possible to include list of users and projects to the response
        """
        end_date = end_date or start_date
        include = include or []
        params = {
            'date[start]': start_date.isoformat(),
            'date[stop]': end_date.isoformat(),
        }
        if include:
            params['include'] = ','.join(include)
        data = self._send_request('GET', f'companies/{organization_id:d}/operations/day', params=params,
                                  list_keys=['daily_activities'] + include)
        return data
