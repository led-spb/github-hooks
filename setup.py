#!/usr/bin/python
import setuptools
import github_events as module

setuptools.setup(
    name=module.name,
    version=module.version,
    author="Alexey Ponimash",
    author_email="alexey.ponimash@gmail.com",
    packages=setuptools.find_packages(exclude=["tests"]),
    install_requires=[],
    scripts=[
        'bin/github-push-trigger.sh.sample'
    ],
    entry_points={
       'console_scripts': [
            'github-events = github_events.console_runner:main'
       ]
    },
)
