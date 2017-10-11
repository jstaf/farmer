from setuptools import (
    find_packages,
    setup,
)


setup(
    name='farmer',
    version='2.1.1',
    author='VM Farms Inc.',
    author_email='support@vmfarms.com',
    url='https://github.com/vmfarms/farmer/',
    description='Deploy your applications on VM Farms.',
    long_description=open('README.md').read(),
    license='Apache 2.0',
    packages=find_packages(),
    install_requires=[
        'click==6.6',
        'layeredconfig==0.3.2',
        'requests==2.11.1',
        'ruamel.yaml==0.13.7',
        'six==1.10.0',
        'stevedore==1.2.0',
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
    ]
)
