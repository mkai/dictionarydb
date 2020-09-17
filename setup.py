import os

from setuptools import find_packages, setup

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
VERSION_FILE = os.path.join(BASE_DIR, "dictionarydb", "__init__.py")
README_FILE = os.path.join(BASE_DIR, "README.rst")

with open(VERSION_FILE) as version_file:
    version_dict = {}
    exec(version_file.read(), version_dict)

with open(README_FILE, encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    name="dictionarydb",
    url="https://github.com/mkai/dictionarydb",
    version=version_dict["__version__"],
    description="Command-line tool to set up a translation dictionary database.",
    long_description=long_description,
    author="Markus Kaiserswerth",
    author_email="github@sensun.org",
    classifiers=[
        "Topic :: Education",
        "Intended Audience :: Education",
    ],
    keywords="education language translations dictionary database importer",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "prettyconf",
        "coloredlogs",
        "click",
        "SQLAlchemy",
        "contexttimer",
        "more-itertools",
        "humanfriendly",
        "iso-639",
    ],
    extras_require={
        "postgresql": ["psycopg2"],
    },
    entry_points={
        "console_scripts": [
            "dictionarydb = dictionarydb.__main__:dictionarydb",
        ],
    },
)
