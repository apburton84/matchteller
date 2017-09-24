# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='matchteller',
    version='0.1.0',
    description='Predict associate football matches',
    long_description=readme,
    author='Anthony Burton',
    author_email='apburton84@googlemail.com',
    url='https://github.com/apburton84/matchteller',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

