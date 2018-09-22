from setuptools import (
    find_packages,
    setup,
)


setup(
    name='farmer',
    version='2.4.1',
    author='VM Farms Inc.',
    author_email='support@vmfarms.com',
    url='https://github.com/vmfarms/farmer/',
    description='Deploy your applications on VM Farms.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='Apache 2.0',
    packages=find_packages(),
    install_requires=[
        'click==6.6',
        'dateparser',
        'layeredconfig==0.3.2',
        'pytz',
        'requests==2.11.1',
        'ruamel.yaml>=0.15.70',
        'sh',
        'six>=1.11.0',
        'stevedore==1.2.0',
        'tzlocal',
    ],
    entry_points={
        'console_scripts': [
            'farmer=farmer.cli:cli',
        ],
        'farmer.commands': [
            'apps = farmer.commands.apps:cli',
            'config = farmer.commands.config:cli',
            'deploy = farmer.commands.deploy:cli',
            'help = farmer.commands.help:cli',
            'logdna = farmer.commands.logdna:cli',
            'version = farmer.commands.version:cli',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ]
)
