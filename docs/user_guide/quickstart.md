# Quick Start Guide


## Installation

In most cases installation via pip is the simplest and best way to install scrapli_cfg.
See [here](/user_guide/installation) for advanced installation details.

```
pip install scrapli-cfg
```


## A Simple Example

```python
from scrapli import Scrapli
from scrapli_cfg import ScrapliCfg

device = {
   "host": "172.18.0.11",
   "auth_username": "vrnetlab",
   "auth_password": "VR-netlab9",
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

```


## More Examples

- [Basic Usage](https://github.com/scrapli/scrapli_cfg/tree/main/examples/basic_usage)
- [Selective Configuration Replace](https://github.com/scrapli/scrapli_cfg/tree/main/examples/selective_config_replace)
