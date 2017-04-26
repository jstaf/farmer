# Farmer

Use `farmer` to deploy your applications on [VM Farms](https://vmfarms.com/).

## Installation

Install with pip:

```
pip install farmer
```

## Configuration

You need to provide Farmer with your VM Farms API token.

Run `farmer config` to set your token for the first time:

```
farmer config
```

If you need to change your token for any reason, you can use `farmer config set token`:

```
farmer config set token c422b5e2230d617d22759a19a5a5cb65792edebc
```

Don't have a token? Contact [VM Farms support](mailto:support@vmfarms.com).

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

## Getting help

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
