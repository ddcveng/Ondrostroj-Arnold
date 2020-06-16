#!/usr/bin/env python

from setuptools import setup

setup(
    name="OndrostrojArnold",
    version="0.1",
    include_package_data=True,
    packages=[
        'engine',
        'player'
    ],
    install_requires=[
        'pyglet'
    ],
    entry_points={
        'console_scripts': [
            'chess=engine.main:main',
        ]}
)