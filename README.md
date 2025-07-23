# upgrade-chromedriver

Bash script to download and update webdriver for Google Chrome.
The webdriver is aimed to support [`selenium`](https://selenium.dev) scrapping library.

Usage:

| Running                       | Result                        |
| ----------------------------- | ----------------------------- |
| `upgrade-chromedriver`        | Check current version of google-chrome and download the matching driver |
| `upgrade-chromedriver --version VERSION` | Check if the driver with the specific version is available |
| `upgrade-chromedriver --apt`  | Check if the driver matching the chrome version to upgrade to is available |

API endpoint in use:<br>
https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json
