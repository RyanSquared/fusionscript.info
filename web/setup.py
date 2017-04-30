#!/usr/bin/env python3

from distutils.core import setup

setup(
    name='fs-info',
    version='0.1.0-1',
    description='Website for displaying information abot stuff and things',
    install_requires=['flask', 'tornado', 'pygments', 'sqlalchemy', 'bcrypt'],
    author='Ryan',
    author_email='vandor2012@gmail.com',
    # url='https://github.com/RyanSquared/',
    packages=['fs-info'])
