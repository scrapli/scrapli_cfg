Changelog
=========

## 2022.01.30

- Revised juniper abort config to remove candidate config file *after* rollback 0 to avoid issues where junos would 
  prompt for confirmation when exiting config mode to go delete the candidate config file prompting timeouts.


## 2021.07.30

- Initial release!
