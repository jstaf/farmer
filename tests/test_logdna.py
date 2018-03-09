import datetime

from freezegun import freeze_time
import pytest
import pytz

from farmer.logdna import epoch


@pytest.mark.parametrize('dt,expected', [
    (datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=pytz.utc), 0),
    (datetime.datetime(2038, 1, 19, 3, 14, 7, tzinfo=pytz.utc), 2**31 - 1),
])
def test_epoch_tz_aware(dt, expected):
    """
    epoch should handle timezone-aware datetimes.
    """
    result = epoch(dt)
    assert result == expected


@freeze_time('2018-01-01T00:00:00')
def test_epoch_tz_naive(mocker):
    """
    epoch should localize timezone-naive datetimes.
    """
    eastern = pytz.timezone('America/Toronto')

    mocked_get_localzone = mocker.patch('tzlocal.get_localzone')
    mocked_get_localzone.return_value = eastern

    now_tz_naive = datetime.datetime.now()
    now_tz_aware = eastern.localize(datetime.datetime.now())

    result_naive = epoch(now_tz_naive)
    result_aware = epoch(now_tz_aware)
    assert result_naive == result_aware


class TestLogDNAClient(object):
    @pytest.mark.parametrize('export_kwargs,payload', [
        (
            {
                'size': 10,
                'levels': 'info,warning',
                'prefer': 'tail',
            },
            {
                'from': 2147483647,
                'to': 2147483647,
                'size': 10,
                'levels': 'info,warning',
                'prefer': 'tail',
            },
        ),
        (
            {
                'size': 0,
                'levels': None,
            },
            {
                'from': 2147483647,
                'to': 2147483647,
                'size': 0,
            },
        ),
    ])
    def test_export_url_params(self, mocker, logdna_client, export_kwargs, payload):
        """
        Should remove invalid URL parameters.
        """
        mocked_epoch = mocker.patch('farmer.logdna.epoch')
        mocked_epoch.return_value = 2147483647

        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(days=1)
        logdna_client.export(yesterday, now, **export_kwargs)
        logdna_client._session.get.assert_called_once_with('https://api.logdna.com/v1/export', params=payload)
