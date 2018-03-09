import pytest


@pytest.fixture
def logdna_client(mocker):
    from farmer.logdna import LogDNAClient
    logdna = LogDNAClient('test service key')
    # Patch the session to mock all network I/O.
    mocker.patch.object(logdna, '_session', autospec=True)
    return logdna


@pytest.fixture
def click_cli_runner():
    from click.testing import CliRunner
    return CliRunner()
