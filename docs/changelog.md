Changelog
=========

## 2022.07.30

- Fix from @WillIrvine to sort a very bad (carl's fault) regex overly aggressive matching -- see #41


## 2022.01.30

- Revised juniper abort config to remove candidate config file *after* rollback 0 to avoid issues where junos would 
  prompt for confirmation when exiting config mode to go delete the candidate config file prompting timeouts.
- Dropped Python3.6 support as it is now EOL! Of course, scrapli probably still works just fine with 3.6 (if you 
  install the old 3.6 requirements), but we won't test/support it anymore.
- Wow, pretty empty here... guess that's a good sign things have been working :p


## 2021.07.30

- Initial release!
