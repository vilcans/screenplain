import os
import re
import json
import configparser


class Defaults:
    FILENAME_CONFIG = 'screenplain.cfg'
    PATH_CONFIG = os.path.join(
        os.getenv('XDG_CONFIG_HOME') or
        os.path.join(os.getenv('HOME'), '.config'),
        'screenplain', FILENAME_CONFIG)


class ConfigurationFileError(Exception):
    pass


class ConfigurationFile(configparser.ConfigParser):
    def __init__(self, path=Defaults.PATH_CONFIG):
        super().__init__(interpolation=None,
                         allow_no_value=True,
                         converters={
                             'list': self.__getlist,
                         })

        # Allow brackets in section names
        self.SECTCRE = re.compile(
            r'^[ \t\r\f\v]*\[(?P<header>.+?)\][ \t\r\f\v]*$')

        # Initialize sections and their expected values
        self.read_string("""
            [export]
                format

                [[pdf]]
                    strong: no
                    font

                [[html]]
                    base: no
                    css

            [font]
        """)

        try:
            self.read(path)
        except configparser.Error as e:
            raise ConfigurationFileError(
                'unable to load configuration file: %s' % e)

    def __getlist(self, v):
        try:
            v = json.loads(v)
        except json.JSONDecodeError as e:
            raise ConfigurationFileError('unable to decode JSON value: %s' % e)

        if not isinstance(v, list):
            raise ConfigurationFileError('value is not a list: %s' % type(v))

        return v
