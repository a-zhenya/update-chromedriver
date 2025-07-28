[![Script Tests](https://github.com/a-zhenya/update-chromedriver/actions/workflows/tests.yaml/badge.svg)](https://github.com/a-zhenya/update-chromedriver/actions/workflows/tests.yaml)

# upgrade-chromedriver

Bash script to download and update webdriver for Google Chrome.
The webdriver is aimed to support [`selenium`](https://selenium.dev) scrapping library.

Usage:

| Running                        | Result                        |
| ------------------------------ | ----------------------------- |
| `upgrade-chromedriver`         | Check current version of google-chrome and download the matching driver |
| `upgrade-chromedriver VERSION` | Check if the driver with the specific version is available |
| `upgrade-chromedriver --apt`   | Check if the driver matching the chrome version to upgrade to is available |

Additional keys:

| Key                      | Effect                        |
| ------------------------ | ----------------------------- |
| `--dry`                  | Dry run, no installation, just check upgrade need and availability of the new version |
| `--download-only`        | Download the zipped driver but do not install |
| `--leave-zip-on-failure` | Do not delete archive if install fails |
| `--target-dir DIR`       | Install chromedriver to this directory |
| `--download-dir DIR`     | Download archive to this directory |
| `--platform PLATFORM`    | Specify the driver platform (default = linux64) |
| `--force`                | Always download |
| `--help`                 | Show usage info |

# Installation
```
curl -L -o update-chromedriver.zip \
    "$(curl -s https://api.github.com/repos/a-zhenya/update-chromedriver/releases/latest | jq -r .zipball_url)"
unzip -j -d $HOME/.local/bin/ update-chromedriver.zip "*/upgrade-chromedriver"
chmod +x $HOME/.local/bin/upgrade-chromedriver
rm -v update-chromedriver.zip
```

# Upgrading
```
upgrade-chromedriver --self-update
```

# Technical Details
API endpoint in use:<br>
https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json

Check this out:<br>
https://deepwiki.com/a-zhenya/update-chromedriver/
