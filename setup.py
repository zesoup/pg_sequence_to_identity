#!/usr/bin/env python3
from setuptools import find_packages, setup

install_requires = [
    'psycopg2-binary',
]

tests_requires=[
    'pytest',
    'pytest-cov',
]

setup(
    name='pg_sequence_to_identity',
    version='1.0.0',
    license='MIT',
    author='Julian Schauder',
    author_email='julian.schauder@credativ.de',
    description='',
    # long_description=readme,
    packages=['pg_sequence_to_identity',],
    zip_safe=False,
    platforms='any',
    install_requires=install_requires,
    tests_requires=tests_requires,
    entry_points={
         'console_scripts': [
             'pg_sti = pg_sti:main',
         ],
     },
)
