# upgrade-chromedriver

Bash script to download and update webdriver for Google Chrome.
The webdriver is aimed to support [`selenium`](https://selenium.dev) scrapping library.

Usage:

| Running                       | Result                        |
| ----------------------------- | ----------------------------- |
| `upgrade-chromedriver`        | Check current version of google-chrome and download the matching driver |
| `upgrade-chromedriver --version VERSION` | Check if the driver with the specific version is available |
| `upgrade-chromedriver --apt`  | Check if the driver matching the chrome version to upgrade to is available |

Additional keys:

| Key                      | Effect                        |
| ------------------------ | ----------------------------- |
| `--help`                 | Show usage info |
| `--dry`                  | Dry run, no installation, just check upgrade need and availability of the new version |
| `--download-only`        | Only download zipped driver |
| `--leave-zip-on-failure` | If extraction fails do not remove the archive |
| `--target-dir DIR`       | Install chromedriver to this directory |

API endpoint in use:<br>
https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json

Check this out:<br>
https://deepwiki.com/a-zhenya/update-chromedriver/
