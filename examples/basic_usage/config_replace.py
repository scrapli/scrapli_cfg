"""scrapli_cfg.examples.basic_usage.config_replace"""
from scrapli import Scrapli
from scrapli_cfg import ScrapliCfg

DEVICE = {
    "host": "localhost",
    "port": 21022,
    "auth_username": "boxen",
    "auth_password": "b0x3N-b0x3N",
    "auth_strict_key": False,
    "platform": "cisco_iosxe",
}


def main():
    """Demo basic config replace functionality"""

    # load up a config to use for the candidate config
    with open("config", "r") as f:
        my_config = f.read()

    # open the "normal" scrapli connection
    with Scrapli(**DEVICE) as conn:
        # create the scrapli cfg object, passing in the scrapli connection, we are also using the
        # scrapli_cfg factory, so we can just pass the connection object and it will automatically
        # find and return the IOSXE (in this case) scrapli-cfg object
        cfg_conn = ScrapliCfg(conn=conn)

        # prepare the scrapli cfg object; this is where we'll fetch the device version and run the
        # `on_prepare` function if provided (to disable logging console or stuff like that)
        cfg_conn.prepare()

        # load up the new candidate config, set replace to True
        cfg_conn.load_config(config=my_config, replace=True)

        # get a diff from the device
        diff = cfg_conn.diff_config()

        # print out the different types of diffs; sometimes the "side by side" and "unified" diffs
        # can be dumb as they only know what you are sending and what is on the device, but have no
        # context about what is getting added or removed. in theory the "device_diff" is smarter
        # because it is what the actual device can give us, though this varies from vendor to vendor
        print(diff.device_diff)
        print(diff.side_by_side_diff)
        print(diff.side_by_side_diff)

        # if you are happy you can commit the config, or if not you can use `abort_config` to abort
        cfg_conn.commit_config()

        # optionally clean it all down when done! this is unnecessary if you are not going to re-use
        # the scrapli cfg object later, but its probably a good habit!
        cfg_conn.cleanup()


if __name__ == "__main__":
    main()
