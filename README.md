[![Supported Versions](https://img.shields.io/pypi/pyversions/scrapli_cfg.svg)](https://pypi.org/project/scrapli_cfg)
[![PyPI version](https://badge.fury.io/py/scrapli-cfg.svg)](https://badge.fury.io/py/scrapli-cfg)
[![Weekly Build](https://github.com/scrapli/scrapli_cfg/workflows/Weekly%20Build/badge.svg)](https://github.com/scrapli/scrapli_cfg/actions?query=workflow%3A%22Weekly+Build%22)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-blueviolet.svg)](https://opensource.org/licenses/MIT)

scrapli_cfg
===========

---

**Documentation**: <a href="https://scrapli.github.io/scrapli_cfg" target="_blank">https://scrapli.github.io/scrapli_cfg</a>

**Source Code**: <a href="https://github.com/scrapli/scrapli_cfg" target="_blank">https://github.com/scrapli/scrapli_cfg</a>

**Examples**: <a href="https://github.com/scrapli/scrapli_cfg/tree/master/examples" target="_blank">https://github.com/scrapli/scrapli_cfg/tree/master/examples</a>

---

scrapli_cfg makes merging or replacing device configurations over Telnet or SSH easy, all while giving you the 
scrapli behaviour you know and love.


#### Key Features:

- __Easy__: It's easy to get going with scrapli and scrapli-cfg -- check out the documentation and example links above, 
  and you'll be managing device configurations in no time.
- __Fast__: Do you like to go fast? Of course you do! All of scrapli is built with speed in mind, but if you really 
  feel the need for speed, check out the `ssh2` transport plugin to take it to the next level! All the "normal" 
  scrapli transport plugin goodness exists here in scrapli-cfg too!
- __Great Developer Experience__: scrapli_cfg has great editor support thanks to being fully typed; that plus 
  thorough docs make developing with scrapli a breeze.


## Requirements

MacOS or \*nix<sup>1</sup>, Python 3.7+

scrapli_cfg's only requirements is `scrapli`.

<sup>1</sup> Although many parts of scrapli *do* run on Windows, Windows is not officially supported


## Installation

```
pip install scrapli-cfg
```

See the [docs](https://scrapli.github.io/scrapli_cfg/user_guide/installation) for other installation methods/details.



## A simple Example

```python
from scrapli import Scrapli
from scrapli_cfg import ScrapliCfg

device = {
   "host": "172.18.0.11",
   "auth_username": "scrapli",
   "auth_password": "scrapli",
   "auth_strict_key": False,
   "platform": "cisco_iosxe"
}

with open("myconfig", "r") as f:
    my_config = f.read()

with Scrapli(**device) as conn:
  cfg_conn = ScrapliCfg(conn=conn)
  cfg_conn.prepare()
  cfg_conn.load_config(config=my_config, replace=True)
  diff = cfg_conn.diff_config()
  print(diff.side_by_side_diff)
  cfg_conn.commit_config()
  cfg_conn.cleanup()

```
