[![Script Tests](https://github.com/a-zhenya/update-chromedriver/actions/workflows/tests.yaml/badge.svg)](https://github.com/a-zhenya/update-chromedriver/actions/workflows/tests.yaml)
[![DeepWiki](https://img.shields.io/badge/DeepWiki-update--chromedriver-blue.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACwAAAAyCAYAAAAnWDnqAAAAAXNSR0IArs4c6QAAA05JREFUaEPtmUtyEzEQhtWTQyQLHNak2AB7ZnyXZMEjXMGeK/AIi+QuHrMnbChYY7MIh8g01fJoopFb0uhhEqqcbWTp06/uv1saEDv4O3n3dV60RfP947Mm9/SQc0ICFQgzfc4CYZoTPAswgSJCCUJUnAAoRHOAUOcATwbmVLWdGoH//PB8mnKqScAhsD0kYP3j/Yt5LPQe2KvcXmGvRHcDnpxfL2zOYJ1mFwrryWTz0advv1Ut4CJgf5uhDuDj5eUcAUoahrdY/56ebRWeraTjMt/00Sh3UDtjgHtQNHwcRGOC98BJEAEymycmYcWwOprTgcB6VZ5JK5TAJ+fXGLBm3FDAmn6oPPjR4rKCAoJCal2eAiQp2x0vxTPB3ALO2CRkwmDy5WohzBDwSEFKRwPbknEggCPB/imwrycgxX2NzoMCHhPkDwqYMr9tRcP5qNrMZHkVnOjRMWwLCcr8ohBVb1OMjxLwGCvjTikrsBOiA6fNyCrm8V1rP93iVPpwaE+gO0SsWmPiXB+jikdf6SizrT5qKasx5j8ABbHpFTx+vFXp9EnYQmLx02h1QTTrl6eDqxLnGjporxl3NL3agEvXdT0WmEost648sQOYAeJS9Q7bfUVoMGnjo4AZdUMQku50McDcMWcBPvr0SzbTAFDfvJqwLzgxwATnCgnp4wDl6Aa+Ax283gghmj+vj7feE2KBBRMW3FzOpLOADl0Isb5587h/U4gGvkt5v60Z1VLG8BhYjbzRwyQZemwAd6cCR5/XFWLYZRIMpX39AR0tjaGGiGzLVyhse5C9RKC6ai42ppWPKiBagOvaYk8lO7DajerabOZP46Lby5wKjw1HCRx7p9sVMOWGzb/vA1hwiWc6jm3MvQDTogQkiqIhJV0nBQBTU+3okKCFDy9WwferkHjtxib7t3xIUQtHxnIwtx4mpg26/HfwVNVDb4oI9RHmx5WGelRVlrtiw43zboCLaxv46AZeB3IlTkwouebTr1y2NjSpHz68WNFjHvupy3q8TFn3Hos2IAk4Ju5dCo8B3wP7VPr/FGaKiG+T+v+TQqIrOqMTL1VdWV1DdmcbO8KXBz6esmYWYKPwDL5b5FA1a0hwapHiom0r/cKaoqr+27/XcrS5UwSMbQAAAABJRU5ErkJggg==)](https://deepwiki.com/a-zhenya/update-chromedriver)

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
curl -L -s \
    "$(curl -s https://api.github.com/repos/a-zhenya/update-chromedriver/releases/latest | jq -r .tarball_url)" \
    | tar xvz --wildcards --strip-components 1 -C $HOME/.local/bin/ "*/upgrade-chromedriver"
chmod +x $HOME/.local/bin/upgrade-chromedriver
```

# Upgrading
```
upgrade-chromedriver --self-update
```

# Technical Details
API endpoint in use:<br>
https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json
