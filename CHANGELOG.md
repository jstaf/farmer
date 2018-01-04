# farmer change log

## 2.3.0 (2018-01-04)

### Added

* Accept configuration from environment variables (`FARMER_<key>`).

### Changed

* Unite `--version` and `version` output.

## 2.2.0 (2017-10-11)

### Added

* `deploy`: Add `-b`/`--branch` argument to deploy specific Git reference. ([#6])

## 2.1.1 (2017-10-11)

### Changes

* `config`: Direct user to portal for API token.

### Fixes

* `config`: Handle empty YAML files. ([#5])

## 2.1.0 (2017-09-11)

### Changes

* `deploy`: Redirect to deploy log after launching deploy. ([#2])

### Fixes

* `config`: Use Python 3 compatible YAML serializer. ([#4])

## 2.0.1 (2017-07-26)

### Fixes

* `config`: Load configuration after first run.

##  2.0.0

Initial public release.

[#2]: https://github.com/vmfarms/farmer/pull/2
[#4]: https://github.com/vmfarms/farmer/issues/4
[#5]: https://github.com/vmfarms/farmer/issues/5
[#6]: https://github.com/vmfarms/farmer/issues/6
