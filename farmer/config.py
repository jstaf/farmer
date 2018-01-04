import codecs
import os

import click
from layeredconfig import (
    Defaults,
    Environment,
    DictSource,
    LayeredConfig,
)
import ruamel.yaml


DEFAULT_CONFIG_DIR = click.get_app_dir('farmer', force_posix=True)
DEFAULTS = {
    'api_url': 'https://my.vmfarms.com/api/v1/',
}


class RoundTripYAMLFile(DictSource):

    def __init__(self, yaml_filename=None, writable=True, **kwargs):
        """
        Loads and optionally saves configuration files in YAML
        format using the ruamel.yaml RoundTripLoader, which preserves comments.

        Args:
            yamlfile (str): The name of a YAML file. Nested
                            sections are turned into nested config objects.
            writable (bool): Whether changes to the LayeredConfig object
                             that has this YAMLFile object amongst its
                             sources should be saved in the YAML file.
        """
        super(RoundTripYAMLFile, self).__init__(**kwargs)
        if yaml_filename is None and 'parent' in kwargs and hasattr(kwargs['parent'], 'yaml_filename'):
            yaml_filename = kwargs['parent'].yaml_filename
        if 'defaults' in kwargs:
            self.source = kwargs['defaults']
        elif kwargs.get('empty', False):
            self.source = {}
        else:
            with codecs.open(yaml_filename, encoding='utf-8') as yaml_file:
                self.source = ruamel.yaml.round_trip_load(yaml_file.read()) or {}
        self.yaml_filename = yaml_filename
        self.dirty = False
        self.writable = writable
        self.encoding = 'utf-8'

    def save(self):
        if self.yaml_filename:
            with codecs.open(self.yaml_filename, 'w', encoding=self.encoding) as yaml_file:
                ruamel.yaml.round_trip_dump(self.source, yaml_file, default_flow_style=False)


def load_config():
    """
    Searches a standard set of locations for .farmer.yml, and parses the first
    match.
    """
    pwd = os.getcwd()
    paths = [os.path.join(pwd, '.farmer.yml'),
             os.path.join(pwd, '.farmer', 'farmer.yml'),
             os.path.join(DEFAULT_CONFIG_DIR, 'farmer.yml')]
    config_file = None
    for path in paths:
        if os.path.exists(path):
            config_file = path
            break
    return LayeredConfig(
        Defaults(DEFAULTS),
        RoundTripYAMLFile(config_file),
        Environment(prefix='FARMER_', sectionsep='__'),
    )
