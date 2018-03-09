# Farmer

[![Build Status](https://travis-ci.org/vmfarms/farmer.svg?branch=master)](https://travis-ci.org/vmfarms/farmer)

Use `farmer` to deploy your applications on [VM Farms](https://vmfarms.com/).

## Installation

Install with pip:

```
pip install farmer
```

## Configuration

You need to provide Farmer with your VM Farms API token. You can retrieve your API token from the [API documentation section](https://my.vmfarms.com/api/) of the VM Farms portal.

Run `farmer config` to set your token for the first time:

```
farmer config
```

If you need to change your token for any reason, you can use `farmer config set token`:

```
farmer config set token c422b5e2230d617d22759a19a5a5cb65792edebc
```

You can also set the token using the `FARMER_TOKEN` environment variable:

```
FARMER_TOKEN=c422b5e2230d617d22759a19a5a5cb65792edebc farmer apps
```

## Usage

### `farmer apps`

Run `farmer apps` to list your  applications.

```
farmer apps
```

If you don't see any applications, we probably need to connect a few wires for you. Contact our [support team](mailto:support@vmfarms.com) and we'll sort you out.

### `farmer deploy`

Run `farmer deploy` to deploy an application:

```
farmer deploy api api-prod
```

### `farmer logdna`

Export logs from [LogDNA](https://logdna.com/) in [JSONLines format](http://jsonlines.org/).

First, generate a [service key](https://app.logdna.com/manage/profile) and configure Farmer:

```
farmer logdna config
```

To export logs, run `farmer logdna export`.
You can filter results by application, host, log level, or a custom search query.

```
# Export all PostgreSQL logs from the past week.
farmer logdna export --from 'last week' --app postgres

# Export deploy logs from today.
farmer logdna export --app deploy
```

The `-f`/`--from` and `-t`/`--to` options support human readable dates like "1 hour ago", "30 minutes ago", "yesterday", etc.
Refer to the [dateparser documentation](https://dateparser.readthedocs.io/en/latest/) for more information.

## Getting help

To get help for a specific command or subcommand, run `farmer help`:

```
farmer help deploy
```

```
farmer help logdna config
```

For bugs or feature requests related to Farmer itself, please open a [GitHub issue](https://github.com/vmfarms/farmer/issues/new).

For issues related to your applications or deploys, please contact [VM Farms support](mailto:support@vmfarms.com).

## Tricks

Add this snippet to your Bash configuration (`~/.bashrc` or `~/.bash_profile`) to enable tab-completion:

```shell
eval "$(_FARMER_COMPLETE=source farmer)"
```

Enjoy!

## License

Apache 2.0
