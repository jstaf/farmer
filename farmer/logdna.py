import datetime

import pytz
import requests
from six.moves.urllib.parse import urljoin
import tzlocal


def epoch(dt):
    """
    Convert a datetime object into seconds since the Unix epoch.

    If `dt` is not timezone-aware, converts it to the local timezone before
    calculating the difference.

    Args:
        dt: datetime

    Returns:
        Seconds since the Unix epoch (int).
    """
    if not dt.tzinfo:
        local_tz = tzlocal.get_localzone()
        dt = local_tz.localize(dt)
    start_of_epoch = datetime.datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    return int((dt - start_of_epoch).total_seconds())


class LogDNAClient(object):
    def __init__(self, service_key, base_url='https://api.logdna.com/v1/'):
        self.service_key = service_key
        self._base_url = base_url
        self._session = requests.Session()
        self._session.auth = (self.service_key, '')

    def export(self, from_datetime, to_datetime, **params):
        """
        Export log lines from LogDNA.

        <https://docs.logdna.com/docs/v1-export-api>

        Args:
            from_datetime (datetime): Start time of logs to export.
            to_datetime (datetime): End time of logs to export.
            **params: URL query parameters passed to export API (refer to API
                documentation).

        Returns:
            Iterator of JSONL lines.

        Raises:
            requests.ConnectionError: There was a network problem communicating
                with LogDNA.
            requests.HTTPError: Request returned an invalid status code.
            requests.Timeout: Request timed out.
        """
        url = urljoin(self._base_url, 'export')
        # Omit empty query parameters.
        payload = {key: value for key, value in params.items() if value is not None}
        payload.update({
            'from': epoch(from_datetime),
            'to': epoch(to_datetime),
        })
        response = self._session.get(url, params=payload)
        response.raise_for_status()
        return response.iter_lines()
