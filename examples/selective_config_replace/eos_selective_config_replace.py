"""scrapli_cfg.examples.basic_usage.eos_selective_config_replace"""
from scrapli import Scrapli
from scrapli_cfg.platform.core.arista_eos import ScrapliCfgEOS
from scrapli_cfg.platform.core.arista_eos.patterns import ETHERNET_INTERFACES

DEVICE = {
    "host": "172.18.0.14",
    "auth_username": "vrnetlab",
    "auth_password": "VR-netlab9",
    "auth_secondary": "VR-netlab9",
    "auth_strict_key": False,
    "platform": "arista_eos",
}


def main():
    """Demo basic selective config replace functionality"""

    # load up a config to use for the candidate config; this config is a bit different though! take
    # a look and you'll see that there are no ethernet interfaces! how can we do a config replace
    # if we have no configuration on any of our ethernet ports?!?! Easy! We can just drop a flag
    # in the configuration that looks an awful lot like a jinja2 variable, in this case:
    # "{{ ethernet_interfaces }}" -- all we need to do is tell scrapli_cfg how to match (from the
    # actual running config) what *should* go in this section (see the next comment section!)
    with open("config", "r", encoding="utf-8") as f:
        my_config = f.read()

    # in this example we have a `dedicated_connection` which means that the scrapli connection is
    # just for scrapli-cfg, when setting `dedicated_connection` to True scrapli cfg will auto open
    # and close the scrapli connection when using a context manager -- or when calling `prepare`
    # and `cleanup`.
    with ScrapliCfgEOS(conn=Scrapli(**DEVICE), dedicated_connection=True) as cfg_conn:
        # the scrapli cfg `render_substituted_config` method accepts a template config, and a list
        # of "substitutes" -- these substitutes are a tuple of the "tag" that needs to be replaced
        # with output from the real device, and a regex pattern that "pulls" this section from the
        # actual device itself. In other words; the "{{ ethernet_interfaces }}" section will be
        # replaced with whatever the provided pattern finds from the real device. clearly the trick
        # here is being good with regex so you can properly snag the section from the real device.
        # In this case there are a handful of already built "patterns" in scrapli cfg you can use,
        # like this ETHERNET_INTERFACES pattern that matches all ethernet interfaces on a device
        # (on a veos at least!) NOTE: this will likely have some changes soon, this is the alpha
        # testing of this!
        rendered_config = cfg_conn.render_substituted_config(
            config_template=my_config, substitutes=[("ethernet_interfaces", ETHERNET_INTERFACES)]
        )
        cfg_conn.load_config(config=rendered_config, replace=True)

        diff = cfg_conn.diff_config()
        print(diff.device_diff)
        print(diff.side_by_side_diff)
        print(diff.side_by_side_diff)

        cfg_conn.commit_config()


if __name__ == "__main__":
    main()
