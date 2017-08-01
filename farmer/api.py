import re

import requests
from six.moves.urllib.parse import (
    urljoin,
    urlparse,
    urlunparse,
)


class VMFarmsAPIError(Exception):
    def __init__(self, message, description=None, response=None, *args, **kwargs):
        super(VMFarmsAPIError, self).__init__(*args, **kwargs)
        self.message = message
        self.description = description
        self.response = response


class VMFarmsAPIClient(object):
    def __init__(self, token, url='https://my.vmfarms.com/', version=1):
        self.url = url
        self.version = version
        self.headers = {'Authorization': 'Token {token}'.format(token=token)}

    @classmethod
    def from_config(cls, config):
        token = config.get(config, 'token')
        api_url = config.get(config, 'api_url')
        parsed_url = urlparse(api_url)
        base_url = urlunparse(parsed_url._replace(path='/'))
        version_match = re.search(r'v(?P<version>\d+)', parsed_url.path)
        try:
            version = version_match.group('version')
        except AttributeError:
            raise VMFarmsAPIError('API URL ({}) must include version.'.format(api_url))
        return cls(token, base_url, version)

    def _request(self, method, path, **kwargs):
        url = self.url_for('api', 'v{self.version}'.format(self=self), *path.split('/'))

        try:
            headers = self.headers.update(kwargs['headers'])
        except KeyError:
            headers = self.headers

        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            raise VMFarmsAPIError('Cannot connect to VM Farms API at {}.'.format(self.url))
        except requests.exceptions.HTTPError as error:
            self._raise_http_error_as_api_error(error)
        except ValueError:
            raise VMFarmsAPIError('Unexpected response from server.', response)

    def url_for(self, *path):
        """
        Construct a version-appropriate API URL for the given path.
        """
        path = [str(item) for item in path]
        # Empty string ensures trailing slash.
        path.append('')
        return urljoin(self.url, '/'.join(path))

    @staticmethod
    def _raise_http_error_as_api_error(error):
        """
        Raise a requests.exceptions.HTTPError as a VMFarmsAPIError.
        """
        errors = {
            requests.codes.FORBIDDEN: ('Could not authenticate.', 'Check your VM Farms token and ask your VM Farms administrator to grant you the Technical Contact role.'),
        }
        try:
            message, description = errors[error.response.status_code]
            raise VMFarmsAPIError(message, description, response=error.response)
        except KeyError:
            raise VMFarmsAPIError('Unexpected response from server.', response=error.response)

    def get(self, *args, **kwargs):
        """
        Read or list resource(s).
        """
        return self._request('GET', *args, **kwargs)

    def post(self, *args, **kwargs):
        """
        Create a resource.
        """
        return self._request('POST', *args, **kwargs)
