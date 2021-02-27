# Project Details


## What is scrapli_cfg

scrapli_cfg is a library that sits "on top" of [scrapli "core"](https://github.com/carlmontanari/scrapli) and 
makes merging or replacing device configurations over Telnet or SSH easy. Why over Telnet or SSH? Because you pretty 
much will always have one of these options available to you, whereas you may not have eAPI or NETCONF ready and 
enabled (think day zero provisioning, or crazy security requirements locking down ports).


### So its like NAPALM?

If you are familiar with the configuration management abilities of the excellent 
[NAPALM library](https://github.com/napalm-automation/napalm) then you are already generally familiar with what 
scrapli_cfg is capable of. The primary differences between scrapli_cfg and NAPALM are as follows:

1. scrapli_cfg has, and never will (unless I change my mind), have "getters" outside the "get_config" and 
   "get_version" getters. This means there will not be anything like "get_interfaces" in scrapli_cfg. 
2. scrapli_cfg has no dependency on any APIs being available -- configurations are all handled via Telnet or SSH. 
   This may sound "bad" because the cli is so "bad", but it means that there are no requirements for additional 
   ports to be opened or services to be enabled (i.e. eAPI or NETCONF), it even means (with a bit of work) you could 
   use scrapli_cfg to fully manage device configuration over console connections.
3. scrapli_cfg has no Python dependencies other than scrapli -- this means there are no vendor libraries necessary, 
   no eznc, no pyeapi, and no pyiosxr. Fewer dependencies isn't a *huge* deal, but it does mean that the scrapli 
   community is fully "in control" of all requirements which is pretty nice!


## Supported Platforms

Just like scrapli "core", scrapli_cfg covers the "core" NAPALM platforms -- Cisco IOS-XE, IOS-XR, NX-OS, 
Arista EOS, and Juniper JunOS (eventually, no JunOS support just yet). Below are the core driver platforms and 
regularly tested version.

Cisco IOS-XE (tested on: 16.12.03)
Cisco NX-OS (tested on: 9.2.4)
Juniper JunOS (tested on: 17.3R2.10)
Cisco IOS-XR (tested on: 6.5.3)
Arista EOS (tested on: 4.22.1F)

Specific platform support requirements are listed below.


### Arista EOS

scrapli_cfg uses configuration sessions in EOS, this feature was added somewhere around the 4.14 release. Early 
versions of EOS that support configuration sessions did not allow configuration sessions to be aborted from 
privilege exec, the `clear_config_sessions` will not work on these versions, however all other scrapli_cfg features 
should work.


### Cisco IOSXE

IOSXE behavior is very similar to NAPALM, using the archive feature to help with config management and diffs, as 
such scrapli_cfg requires IOS versions > 12.4(20)T -- all IOSXE versions *should* be supported (please open an issue 
or find me on Slack/Twitter if this is incorrect!).


### Cisco IOSXR

scrapli_cfg has worked on every IOSXR version that it has been tested on -- due to IOSXR natively supporting 
configuration merging/replacing this *should* work on most IOSXR devices.


### Cisco NXOS

scrapli_cfg *should* work on most versions of NXOS, there is no requirement for NX-API, instead scrapli_cfg simply 
relies on the tclsh.


### Juniper JunOS

JunOS is not supported... *yet*... this section will updated when support is added!
