from setuptools import find_packages, setup

setup(
    name="strut-web",
    version="1.0.0.dev0",
    packages=find_packages("."),
    entry_points={"console_scripts": ["strut=strut.cli:main"]},
)
