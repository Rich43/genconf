#!/usr/bin/python3
from setuptools import setup, find_packages

requires = [
    'jinja2',
]

setup(name='genconf',
      version='0.1',
      description='Configuration File Generator',
      author='Richie Ward',
      author_email='RichieS@GMail.com',
      url='http://pynguins.com/',
      packages=['genconf'],
      install_requires=requires
)
