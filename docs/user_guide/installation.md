# Installation


## Standard Installation

As outlined in the quick start, you should be able to pip install scrapli "normally":

```
pip install scrapli-cfg
```


## Installing current master branch

To install from the source repositories master branch:

```
pip install git+https://github.com/scrapli/scrapli_cfg
```


## Installing current develop branch

To install from the source repositories develop branch:

```
pip install -e git+https://github.com/scrapli/scrapli_cfg.git@develop#egg=scrapli_cfg
```


## Installation from Source

To install from source:

```
git clone https://github.com/scrapli/scrapli_cfg
cd scrapli_cfg
python setup.py install
```


## Supported Platforms

As for platforms to *run* scrapli on -- it has and will be tested on MacOS and Ubuntu regularly and should work on any
 POSIX system. Windows at one point was being tested very minimally via GitHub Actions builds, however this is no
  longer the case as it is just not worth the effort. While scrapli should work on Windows when using the paramiko or
   ssh2-python transport drivers, it is not "officially" supported. It is *strongly* recommended/preferred for folks
    to use WSL/Cygwin instead of Windows.
