import os
import ConfigParser
from setuptools import setup, find_packages


def default_config():
    conf = os.path.join(os.path.expanduser('~'), '.dasher.ini')

    if not os.path.exists(conf):
        config = ConfigParser.ConfigParser()
        config.add_section('credentials')
        config.set('credentials', 'username', '')
        config.set('credentials', 'password', '')

        config.add_section('influxdb')
        config.set('influxdb', 'database_uri', '')

        with open(conf, 'w') as configfile:
            config.write(configfile)
    
    return conf


conf = default_config()

setup(name='dasher',
      version='1.0',
      description='Tool to gather data from various resources and upload it to influxdb',
      author='Justin Anderson',
      author_email='justin.ta@outlook.com',
      license='MIT',
      packages=find_packages(),
      data_files=[conf],
      install_requires=[
          'gitpython'
      ],
      scripts=[
          'bin/dasher'
      ])
