#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages
from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    # TODO: put package requirements here
    'python-redmine',
    'requests',
    'beautifulsoup4',
    'python-creole',
    'html2text',
]

test_requirements = [
    # TODO: put package test requirements here
]

extra_requirements={
    'docs': [
        'Sphinx',
    ],
    'release': [
        'zest.releaser',
    ],
    'develop': [
        'pdbpp',
        'isort',
    ],
}

setup(
    name='trac_redmine_importer',
    version='0.1.0',
    description="Python Boilerplate contains all the boilerplate you need to create a Python package.",
    long_description=readme + '\n\n' + history,
    author="Alexander Loechel",
    author_email='Alexander.Loechel@gmail.com',
    url='https://github.com/loechel/trac_redmine_importer',
    #packages=[
    #    'trac_redmine_importer',
    #],
    #package_dir={'trac_redmine_importer':
    #             'trac_redmine_importer'},
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'trac_redmine_importer=trac_redmine_importer.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    extras_require=extra_requirements,
    license="MIT license",
    zip_safe=False,
    keywords='trac_redmine_importer',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
