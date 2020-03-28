# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

exec(open('etesync/_version.py').read())

setup(
    name='etesync',
    version=__version__,
    author='Tom Hacohen',
    author_email='tom@stosb.com',
    url='https://github.com/etesync/pyetesync',
    description='Python client library for EteSync',
    keywords=['etesync', 'encryption', 'sync', 'pim'],
    license='LGPL-3.0-only',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[
        'appdirs>=1.4',
        'asn1crypto>=0.22',
        'cffi>=1.10',
        'cryptography>=1.9',
        'furl>=0.5',
        'idna>=2.5',
        'orderedmultidict>=0.7',
        'packaging>=16.8',
        'peewee>=3.7.0',
        'py>=1.4',
        'pyasn1>=0.2',
        'pycparser>=2.17',
        'pyparsing>=2.2',
        'scrypt>=0.8.13',  # pyscrypt is also supported as a fallback, but better to use scrypt
        'python-dateutil>=2.6',
        'pytz>=2019.1',
        'requests>=2.21',
        'six>=1.10',
        'vobject>=0.9',
    ]
)
