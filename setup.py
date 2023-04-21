#!/usr/bin/env python

"""The setup script."""
from setuptools import find_packages, setup

with open("README.md") as readme_file:
    readme = readme_file.read()

requirements = ["typer", "playwright", "appdirs", "empack >=3.0.0", "rich"]

setup(
    author="Thorsten Beier",
    author_email="derthorstenbeier@gmail.com",
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    include_package_data=True,
    description="pyjs_code_runner emscripten+boa",
    entry_points={
        "console_scripts": [
            "pyjs_code_runner=pyjs_code_runner.cli.app:app",
        ],
    },
    install_requires=requirements,
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords="pyjs_code_runner",
    name="pyjs_code_runner",
    packages=find_packages(),
    url="https://github.com/emscripten-forge/pyjs_code_runner",
    version="2.0.0",
    zip_safe=False,
)
