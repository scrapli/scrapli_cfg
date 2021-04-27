# Basic Usage


## Picking the right Driver

When using scrapli_cfg, you will need to ensure that you are building a scrapli_cfg object specific to the target 
device. You can create your connection object directly from the appropriate scrapli_cfg class, i.e., 
`ScrapliCfgIOSXE`, or you can use the "factory" function to appropriately dispatch the class type based on a provided 
`conn` object (scrapli connection object). A simple example of creating a scrapli_cfg object by both methods is below:

```python

from scrapli import Scrapli
from scrapli_cfg.platform.core.cisco_iosxe import ScrapliCfgIOSXE
from scrapli_cfg import ScrapliCfg

device = {
   "host": "172.18.0.11",
   "auth_username": "vrnetlab",
   "auth_password": "VR-netlab9",
   "auth_strict_key": False,
   "platform": "cisco_iosxe"
}
conn = Scrapli(**device)
cfg_conn_from_specific_platform_class = ScrapliCfgIOSXE(conn=conn)
cfg_conn_from_factory = ScrapliCfg(conn=conn)
```

The available platform names are:

- `arista_eos`
- `cisco_iosxe`
- `cisco_iosxr`
- `cisco_nxos`
- `juniper_junos`


## Driver Arguments

scrapli_cfg doesn't have a ton of arguments/options that you need to worry about! The most important argument is the 
`conn` argument -- which is expecting a scrapli connection that is built from the `NetworkDriver`. This connection 
must be from one of the "core" scrapli platforms (EOS, IOSXE, IOSXR, NXOS, JunOS).

The other remaining primary arguments are as follows:

- `config_sources`: Generally ignored/handled by the platform implementation for you. A list of strings representing 
  the valid config sources, i.e. "running", "candidate", or "startup"
- `on_prepare`: A callable (sync or async depending on your code of course) that is executed during the `prepare` 
  method; initially scrapli-cfg contained a default callable that would disable console logging (in most cases), 
  however as this actually made changes to your device that were somewhat "magic" it was removed. Now, users can 
  pass an `on_prepare` callable to disable console logging, or really anything else they want. This callable should 
  accept `cls` as the first argument which is a reference to the scrapli-cfg object itself (and thus has access to 
  the underlying scrapli connection). More on this in the [`on_prepare` section](#on-prepare).
- `dedicated_connection`: If `False` (default value) scrapli cfg will not open or close the underlying scrapli 
  connection and will raise an exception if the scrapli connection is not open. If `True` will automatically open 
  and close the scrapli connection when using with a context manager, `prepare` will open the scrapli connection (if 
  not already open), and `close` will close the scrapli connection.
- `ignore_version`: Ignore checking device version support; currently this just means that scrapli-cfg will not 
  fetch the device version during the prepare phase, however this will (hopefully) be used in the future to limit 
  what methods can be used against a target device. For example, for EOS devices we need > 4.14 to load configs; so 
  if a device is encountered at 4.13 the version check would raise an exception rather than just failing in a 
  potentially awkward fashion.

There are no additional arguments for creating a scrapli_cfg object, though each platform may have other 
optional arguments as necessary -- check the docs/class for those.


## scrapli_cfg Methods

scrapli_cfg methods are mostly intended at managing device configuration, though there are a few extra methods in 
there as well. The following sections provide a brief description and example of how to use the main public methods.

Note that nearly all public methods in scrapli_cfg will return a `ScrapliCfgResponse` object that will contain a 
`result` attribute of the result of the given task, as well as the underlying scrapli `Response` object, and the 
usual scrapli attributes like start/finish/elapsed time, a `failed` attribute, and a `raise_for_status` method.


### Get Version

The `get_version` method does exactly what you would expect it to -- it fetches the version string from the target 
device. scrapli_cfg very intentionally has no "getters" (in the NAPALM-sense) except for `get_version` 
and `get_config` -- this is because there is no desire to maintain support for getters across a huge variety of 
versions/platforms. That said, the `get_version` method was implemented in order to (obviously) fetch device 
versions to (in the future) be used to validate the target device version supports all features that scrapli_cfg 
needs in order to manage the configurations. 

A simple example of fetching and printing the device version:

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
with Scrapli(**device) as conn:
    cfg_conn = ScrapliCfg(conn=conn)
    cfg_conn.prepare()
    version_result = cfg_conn.get_version()
    print(version_result.result)
```


### Get Config

The `get_config` method does exactly what you would think it does, it fetches the device configuration as a string. 
This method supports a `source` argument to which you can provide a string representing the source config you would 
like to get -- generally this will be either "startup" or "running".

A simple example of fetching and printing the device startup configuration:

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
with Scrapli(**device) as conn:
    cfg_conn = ScrapliCfg(conn=conn)
    cfg_conn.prepare()
    cfg_result = cfg_conn.get_config(source="startup")
    print(cfg_result.result)
```


### Get Checkpoint (NXOS Only)

NXOS can be a little... difficult with configuration replacement operations. It expects to be fed "checkpoint" files 
instead of "normal" configuration text. In order to make life a bit easier the NXOS platform supports a 
`get_checkpoint` method that fetches a checkpoint file from the device. This is basically the same overall behavior 
as `get_config`, just resulting in fetching a checkpoint file. Some details about checkpoints can be found 
[here](https://www.cisco.com/c/en/us/td/docs/switches/datacenter/nexus9000/sw/6-x/system_management/configuration/guide/b_Cisco_Nexus_9000_Series_NX-OS_System_Management_Configuration_Guide/sm_7rollback.html).

A simple example of fetching and printing a checkpoint file from an NXOS device:

```python

from scrapli import Scrapli
from scrapli_cfg import ScrapliCfg

device = {
   "host": "172.18.0.12",
   "auth_username": "vrnetlab",
   "auth_password": "VR-netlab9",
   "auth_strict_key": False,
   "platform": "cisco_nxos"
}
with Scrapli(**device) as conn:
    cfg_conn = ScrapliCfg(conn=conn)
    cfg_conn.prepare()
    chkpoint_result = cfg_conn.get_checkpoint()
    print(chkpoint_result.result)
```


### Load Config

Another, hopefully very obviously named method! `load_config` does what it sounds like. `load_config` accepts a 
configuration to load (as a string; note that if you are doing config replace with NXOS you should use a checkpoint 
file!), optionally a bool indicating if the operation is a "replace" operation (default is `False` it is a *merge* 
operation), and lastly some optional keyword arguments that vary from platform to platform.

If `replace` is `False` (default) then the config will be loaded as a *merge* candidate, otherwise it will be loaded 
as a full *replace* candidate.

```python

from scrapli import Scrapli
from scrapli_cfg import ScrapliCfg

with open("config", "r") as f:
    my_config = f.read()

device = {
   "host": "172.18.0.11",
   "auth_username": "vrnetlab",
   "auth_password": "VR-netlab9",
   "auth_strict_key": False,
   "platform": "cisco_iosxe"
}
with Scrapli(**device) as conn:
    cfg_conn = ScrapliCfg(conn=conn)
    cfg_conn.prepare()
    load_result = cfg_conn.load_config(config=my_config, replace=True)
    print(load_result)
```

Note that *loading* a configuration does *not* apply the configuration! This simply will create a configuration 
session or a file on the device (depending on the specific platform type) that can be used to merge/replace the config.


### Abort Config

If you've loaded a configuration but don't want to commit it, you can call `abort_config` which will delete the 
candidate config/delete config sessions used to load the config.


```python

from scrapli import Scrapli
from scrapli_cfg import ScrapliCfg

with open("config", "r") as f:
    my_config = f.read()

device = {
   "host": "172.18.0.11",
   "auth_username": "vrnetlab",
   "auth_password": "VR-netlab9",
   "auth_strict_key": False,
   "platform": "cisco_iosxe"
}
with Scrapli(**device) as conn:
    cfg_conn = ScrapliCfg(conn=conn)
    cfg_conn.prepare()
    load_result = cfg_conn.load_config(config=my_config, replace=True)
    print(load_result)
    abort_result = cfg_conn.abort_config()
    print(abort_result)
```


### Commit Config

If you've loaded a config and want to save/commit it you can do so with the `commit_config` method:

```python

from scrapli import Scrapli
from scrapli_cfg import ScrapliCfg

with open("config", "r") as f:
    my_config = f.read()

device = {
   "host": "172.18.0.11",
   "auth_username": "vrnetlab",
   "auth_password": "VR-netlab9",
   "auth_strict_key": False,
   "platform": "cisco_iosxe"
}
with Scrapli(**device) as conn:
    cfg_conn = ScrapliCfg(conn=conn)
    cfg_conn.prepare()
    load_result = cfg_conn.load_config(config=my_config, replace=True)
    print(load_result)
    commit_result = cfg_conn.commit_config()
    print(commit_result)
```


### Diff Config

Perhaps the most interesting/handy method of all: `diff_config`! Just like the other methods, this method does 
exactly what it sounds like it would. There is one important difference between this method and the others, however; 
the `diff_config` method returns a `ScrapliCfgDiffResponse` object instead of a `ScrapliCfgResponse` object. The 
`ScrapliCfgDiffResponse` object is *mostly* the same as a normal scrapli_cfg response, but it also contains some 
properties that contain the diff output.

scrapli_cfg always tries to get a diff from the device itself -- from whatever means are available on box, but also 
builds some basic diffs of its own. The diffs that scrapli_cfg builds are fairly simple and will show the difference 
between the candidate config and the target config, but will have no context about merge vs replace operations, so 
the diff will always show the "full" configuration diff (with colorful output though!). 

You can see each of the diffs like so:

```python

from scrapli import Scrapli
from scrapli_cfg import ScrapliCfg

with open("config", "r") as f:
    my_config = f.read()

device = {
   "host": "172.18.0.11",
   "auth_username": "vrnetlab",
   "auth_password": "VR-netlab9",
   "auth_strict_key": False,
   "platform": "cisco_iosxe"
}
with Scrapli(**device) as conn:
    cfg_conn = ScrapliCfg(conn=conn)
    cfg_conn.prepare()
    load_result = cfg_conn.load_config(config=my_config, replace=True)
    print(load_result)
    diff_result = cfg_conn.diff_config()
    print(diff_result.device_diff)
    print(diff_result.unified_diff)
    print(diff_result.side_by_side_diff)
```


### Render Substituted Config

The `render_substituted_config` method is used to (based on user provided regex) auto merge a candidate 
configuration with sections of the current device configuration. This is meant to allow users an easy-ish way to 
start doing config replace operations, without having to have a template that covers all aspects of the device 
configuration.

For example, let's say you want to manage everything on a switch *except* the interfaces. Maybe you want to do this 
because managing loads of templates for all the different types of interfaces/platforms is a pain, or maybe a 
different team manages that part of the config... whatever the case you want to be able to do full config replaces, 
but leave that part of the config completely untouched. This is what the `render_substitued_config` method is 
designed to help you with.

Here is an example of using this method:

```python

from scrapli import Scrapli
from scrapli_cfg import ScrapliCfg
from scrapli_cfg.platform.core.arista_eos.patterns import ETHERNET_INTERFACES


with open("config", "r") as f:
    my_config = f.read()

device = {
   "host": "172.18.0.14",
   "auth_username": "vrnetlab",
   "auth_password": "VR-netlab9",
   "auth_strict_key": False,
   "platform": "arista_eos"
}
with Scrapli(**device) as conn:
    cfg_conn = ScrapliCfg(conn=conn)
    cfg_conn.prepare()
    rendered_config = cfg_conn.render_substituted_config(
        config_template=my_config, substitutes=[("ethernet_interfaces", ETHERNET_INTERFACES)]
    )
    load_result = cfg_conn.load_config(config=my_config, replace=True)
    print(load_result)
```

In the above example we have a fairly "normal" scrapli_cfg setup -- create a connection and open it. Once the 
connection is opened we call the `render_substituted_config` and we pass a `config_template` and a list of 
`substitutes` to it. The config template is what it sounds like -- a template (that looks like a jinja2 template). 
In this case, this template has a variable `ethernet_interfaces` in the file where the ethernet interfaces *would* 
go, so instead of something like this:

```
username vrnetlab role network-admin secret sha512 $6$8zrJ4ESW2fqG2QqH$9u768TvLXXDeUJmG2Std71EX1ip6q4MoJrMwDng1cmpuSYc9ECWytRjvXpMH7C3dzSdoEv0MxAUiAZeeTre3h.
!
interface Ethernet 1
  description tacocat
!
<< SNIP >>
interface Management1
```

We have something like this:

```
username vrnetlab role network-admin secret sha512 $6$8zrJ4ESW2fqG2QqH$9u768TvLXXDeUJmG2Std71EX1ip6q4MoJrMwDng1cmpuSYc9ECWytRjvXpMH7C3dzSdoEv0MxAUiAZeeTre3h.
!
{{ ethernet_interfaces }}
interface Management1
```

The `substitutes` we passed into the `render_substituted_config` method is a list of tuples, where the first item in 
the tuple is the variable we want to replace (`ethernet_interfaces` in this case) and the second value is a regular 
expression that matches the section of the real running config that we want to put into this variable.

Ultimately, using this example, if we had a "real" running configuration containing the following interface section 
(just using one interface to keep things simple) that looked like this:

```
username vrnetlab role network-admin secret sha512 $6$8zrJ4ESW2fqG2QqH$9u768TvLXXDeUJmG2Std71EX1ip6q4MoJrMwDng1cmpuSYc9ECWytRjvXpMH7C3dzSdoEv0MxAUiAZeeTre3h.
!
interface Ethernet 1
  description tacocat
!
interface Management1
```

Our rendered template would end up looking just like that. Again, the point of this method is to allow you to more 
easily do configuration replaces without having to fully template out device configs. The obvious downside to this 
method is that it may require fairly complicated regular expressions in order to properly slice and dice the real 
config.



## On Prepare

The `on_prepare` argument of the scrapli-cfg objects gives users the opportunity to pass a callable that will be 
executed prior to any operations occurring (this happens during the aptly named "prepare" method which you should be 
calling prior to using scrapli_cfg operations -- note that if you use the context manager functionality this will 
already be called for you!). The purpose of this `on_prepare` callable is to... prepare a device for config 
operations. Initially scrapli_cfg platforms contained a sane default `on_prepare` function that basically just 
disabled console logging. The reasoning for disabling console logging is to ensure that any `get_config` operations 
don't have log messages garbling up the output.

This "sane default" setting has since been removed as it was a bit too much "magic" -- meaning that it felt wrong 
for scrapli_cfg to be making any kind of persistent configuration changes to your devices potentially without users 
being aware that was happening. As such, it would be a good idea to provide an `on_prepare` callable to at the very 
least disable console logging.
