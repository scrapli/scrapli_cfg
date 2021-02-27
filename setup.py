#!/usr/bin/env python
"""scrapli_cfg - configuration management with scrapli"""
import setuptools

__author__ = "Carl Montanari"
__version__ = "2021.07.30a2"

with open("README.md", "r", encoding="utf-8") as f:
    README = f.read()

with open("requirements.txt", "r") as f:
    INSTALL_REQUIRES = f.read().splitlines()

setuptools.setup(
    name="scrapli_cfg",
    version=__version__,
    author=__author__,
    author_email="carl.r.montanari@gmail.com",
    description="Configuration management with scrapli",
    long_description=README,
    long_description_content_type="text/markdown",
    keywords="ssh telnet netconf automation network cisco iosxr iosxe nxos arista eos juniper "
    "junos",
    url="https://github.com/scrapli/scrapli_cfg",
    project_urls={
        "Changelog": "https://scrapli.github.io/scrapli_cfg/changelog",
        "Docs": "https://scrapli.github.io/scrapli_cfg/",
    },
    license="MIT",
    packages=setuptools.find_packages(),
    install_requires=INSTALL_REQUIRES,
    extras_require={},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
)
