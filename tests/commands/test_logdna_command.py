import dateparser
import freezegun
import pytest
import requests

from farmer.commands import logdna


class TestLogDNAConfigCommand(object):
    @pytest.fixture(autouse=True)
    def click_cli_runner(self, request, click_cli_runner):
        self.click_cli_runner = click_cli_runner

    @pytest.fixture(autouse=True)
    def mocks(self, request, mocker):
        self.mocked_config = mocker.MagicMock()
        self.mocked_load_config = mocker.patch('farmer.commands.logdna.load_config')
        self.mocked_load_config.return_value = self.mocked_config
        # Do not actually run `farmer config`.
        self.mocked_sh = mocker.patch('farmer.commands.logdna.sh')

    def test_new_service_key(self):
        """
        `logdna config` should set service key if none exists.
        """
        self.mocked_config.get.return_value = None

        result = self.click_cli_runner.invoke(logdna.config, input='test service key\n')

        assert result.exit_code == 0
        assert not result.exception
        self.mocked_load_config.assert_called_once_with()
        self.mocked_config.get.assert_called_once_with(self.mocked_config, 'logdna_service_key')
        self.mocked_sh.farmer.config.set.assert_called_once_with('logdna_service_key', 'test service key')

    def test_overwrite_service_key(self):
        """
        `logdna config` should overwrite the service key with confirmation.
        """
        self.mocked_config.get.return_value = 'existing service key'

        result = self.click_cli_runner.invoke(logdna.config, input='test service key\ny\n')

        assert result.exit_code == 0
        assert not result.exception
        self.mocked_load_config.assert_called_once_with()
        self.mocked_config.get.assert_called_once_with(self.mocked_config, 'logdna_service_key')
        self.mocked_sh.farmer.config.set.assert_called_once_with('logdna_service_key', 'test service key')

    def test_no_overwrite_service_key(self):
        """
        `logdna config` should not overwrite the service key without confirmation.
        """
        self.mocked_config.get.return_value = 'existing service key'

        result = self.click_cli_runner.invoke(logdna.config, input='test service key\nn\n')

        assert result.exit_code == 1
        assert result.exception
        self.mocked_load_config.assert_called_once_with()
        self.mocked_config.get.assert_called_once_with(self.mocked_config, 'logdna_service_key')
        self.mocked_sh.farmer.config.set.assert_not_called()


class TestLogDNAExportCommand(object):
    @pytest.fixture(autouse=True)
    def click_cli_runner(self, request, click_cli_runner):
        self.click_cli_runner = click_cli_runner

    @pytest.fixture(autouse=True)
    def mocks(self, request, mocker, logdna_client):
        self.mocked_config = mocker.MagicMock()
        self.mocked_config.get.return_value = 'existing service key'
        self.mocked_load_config = mocker.patch('farmer.commands.logdna.load_config')
        self.mocked_load_config.return_value = self.mocked_config

        # Replace LogDNAClient with patched version.
        self.logdna_client = logdna_client
        mocker.patch.object(logdna_client, 'export')
        MockLogDNAClient = mocker.patch('farmer.commands.logdna.LogDNAClient')
        MockLogDNAClient.return_value = self.logdna_client

    def test_no_service_key(self, mocker):
        """
        `logdna export` should prompt for a service key if no key exists.
        """
        self.mocked_config.get.return_value = None
        mocked_prompt_logdna_service_key = mocker.patch('farmer.commands.logdna.prompt_logdna_service_key')
        mocked_prompt_logdna_service_key.return_value = None

        result = self.click_cli_runner.invoke(logdna.export)

        mocked_prompt_logdna_service_key.assert_called_once_with()
        self.logdna_client.export.assert_called_once()
        assert result.exit_code == 0
        assert not result.exception

    def test_service_key(self, mocker):
        """
        `logdna export` should not prompt for a service key if one exists.
        """
        mocked_prompt_logdna_service_key = mocker.patch('farmer.commands.logdna.prompt_logdna_service_key')

        result = self.click_cli_runner.invoke(logdna.export)

        mocked_prompt_logdna_service_key.assert_not_called()
        self.logdna_client.export.assert_called_once()
        assert result.exit_code == 0
        assert not result.exception

    def test_handle_api_error(self, mocker):
        """
        `logdna export` should exit on an API error.
        """
        self.logdna_client.export.side_effect = requests.RequestException()

        result = self.click_cli_runner.invoke(logdna.export)

        assert result.exit_code == 1
        assert result.exception

    def test_output(self, mocker):
        """
        `logdna export` should stream log lines.
        """
        lines = [
            '{"example": "line 1"}',
            '{"example": "line 2"}',
            '{"example": "line 3"}',
        ]
        self.logdna_client.export.return_value = lines

        result = self.click_cli_runner.invoke(logdna.export)

        assert result.exit_code == 0
        assert not result.exception
        assert result.output == '\n'.join(lines) + '\n'

    @pytest.mark.parametrize('from_datetime', [
        'now',
        'yesterday'
        '1 day ago',
        '1 hour ago',
        '30 minutes ago',
    ])
    @freezegun.freeze_time('2018-01-01T00:00:00')
    def test_valid_datetime(self, mocker, from_datetime):
        """
        `logdna export` should handle valid human readable dates.
        """
        # Testing the parsed datetime result is not feasible. dateparser uses
        # tzlocal.get_localzone() to localize datetimes, which will differ
        # between test machines. Patching that call requires knowledge about
        # dateparser internals.
        # Instead, test that dateparser *can* parse the string and the callback
        # passes it to `from_datetime`.
        result = self.click_cli_runner.invoke(logdna.export, ['--from', from_datetime])

        assert result.exit_code == 0
        assert not result.exception
        self.logdna_client.export.assert_called_once_with(
            from_datetime=dateparser.parse(from_datetime),
            to_datetime=mocker.ANY,
            size=mocker.ANY,
            hosts=mocker.ANY,
            apps=mocker.ANY,
            levels=mocker.ANY,
            query=mocker.ANY,
            prefer=mocker.ANY,
        )

    @pytest.mark.parametrize('from_datetime', [
        'some invalid date string',
    ])
    def test_invalid_input(self, mocker, from_datetime):
        """
        `logdna export` should raise an exception for invalid dates.
        """
        result = self.click_cli_runner.invoke(logdna.export, ['--from', from_datetime])

        assert result.exit_code == 1
        assert result.exception
        self.logdna_client.export.assert_not_called()
