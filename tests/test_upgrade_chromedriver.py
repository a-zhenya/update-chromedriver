import subprocess as sp
from pathlib import Path
import os
import pytest

OLD_VERSION = "1.1.1.1"
NEW_VERSION = "2.2.2.2"


class MockApps:
    def __init__(self, path: Path):
        self.path = path

    def install_chrome(self, version):
        (self.path / "google-chrome").write_text(f"#!/bin/bash\necho Google Chrome {version}\n")
        (self.path / "google-chrome").chmod(0o755)

    def install_chromedriver(self, version):
        (self.path / "chromedriver").write_text(f"#!/bin/bash\necho ChromeDriver {version} '(hash)'\n")
        (self.path / "chromedriver").chmod(0o755)

    def install_curl(self, create_file: bool, success_code: bool):
        script = """#!/bin/bash
while [ $# -gt 0 ]; do
    if [ "$1" = "-o" ]; then shift; FILE="$1"; fi
    URL="$1" # URL is the last argument
    shift
done
if [ -n "$FILE" ]; then
    echo $URL > "$FILE"
fi
"""
        (self.path / "curl").write_text(
            (script if create_file else "#!/bin/bash\nexit 0\n") if success_code else "#!/bin/bash\nexit 1\n"
        )
        (self.path / "curl").chmod(0o755)

    def install_jq(self, success: bool):
        script = """#!/bin/bash
while [ $# -gt 0 ]; do
    case "$1" in
        PLATFORM)
            shift
            PLATFORM="$1"
            ;;
        VERSION)
            shift
            VERSION="$1"
            ;;
    esac
    shift
done
echo http://example.com/downloads/$VERSION/$PLATFORM/chromedriver.zip
"""
        (self.path / "jq").write_text(script if success else "#!/bin/bash\nexit 0\n")
        (self.path / "jq").chmod(0o755)

    def install_unzip(self, verify: bool, success: bool):
        verification_return = "0" if verify else "1"
        unzip_return = "0" if success else "1"
        script = f"""#!/bin/bash
ZIP=""
while [ $# -gt 0 ]; do
    case "$1" in
        -t)
            exit {verification_return}
            ;;
        -d)
            shift
            DIR="$1"
            ;;
        -*)
            # Ignore other options
            ;;
        *)
            if [ -z "$ZIP" ]; then
                ZIP="$1"
            fi
            ;;
    esac
    shift
done
if [ {unzip_return} -ne 0 ]; then
    exit {unzip_return}
fi
cat "$ZIP" > "$DIR/chromedriver"
"""
        (self.path / "unzip").write_text(script)
        (self.path / "unzip").chmod(0o755)

    def mock_apt(self, version):
        out = f'echo "Conf google-chrome-stable {version}"' if version else ""
        (self.path / "apt-get").write_text(f"#!/bin/bash\n{out}\n")
        (self.path / "apt-get").chmod(0o755)

    def install_tools(
        self, curl_download=True, curl_success=True, jq_success=True, unzip_verify=True, unzip_success=True
    ):
        self.install_curl(curl_download, curl_success)
        self.install_jq(jq_success)
        self.install_unzip(unzip_verify, unzip_success)


def run_upgrade(
    *,
    args=None,
    env=None,
    chrome=NEW_VERSION,
    chromedriver=OLD_VERSION,
    tools=True,
    update_found=True,
    curl_download=True,
    curl_success=True,
    apt_version=NEW_VERSION,
    unzip_success=True,
    unzip_verify=True,
    wrkdir=".",
):
    save_cwd = Path.cwd()
    (Path(wrkdir) / "cwd").mkdir(parents=True, exist_ok=True)
    os.chdir(Path(wrkdir) / "cwd")
    args = ["bash", save_cwd / "upgrade-chromedriver"] + (args or [])
    bindir = Path(wrkdir) / "bin"
    bindir.mkdir(exist_ok=True)
    for tool in ["bash", "cat", "grep", "chmod", "cut", "touch", "rm", "ls", "dirname", "mktemp"]:
        os.symlink(f"/bin/{tool}", bindir / tool)

    mock = MockApps(bindir)
    if chrome:
        mock.install_chrome(chrome)
    if chromedriver:
        mock.install_chromedriver(chromedriver)
    if tools:
        mock.install_tools(
            curl_download=curl_download,
            curl_success=curl_success,
            jq_success=update_found,
            unzip_verify=unzip_verify,
            unzip_success=unzip_success,
        )
    mock.mock_apt(apt_version)

    homedir = Path(wrkdir) / "home"
    (homedir / ".local" / "bin").mkdir(parents=True, exist_ok=True)
    if not env:
        env = {}
    env.update({"HOME": str(homedir), "PATH": str(bindir)})
    res = sp.run(args, text=True, stdin=sp.DEVNULL, stdout=sp.PIPE, stderr=sp.PIPE, env=env), bindir, homedir
    os.chdir(save_cwd)
    return res


# === POSITIVE PATHS ===


def test_new_driver(tmp_path):  # no chromedriver before
    res, bindir, homedir = run_upgrade(chromedriver=False, wrkdir=tmp_path)
    assert (homedir / ".local" / "bin" / "chromedriver").exists()
    assert os.access(homedir / ".local" / "bin" / "chromedriver", os.X_OK)
    assert res.returncode == 0


def test_replace_driver(tmp_path):  # default upgrade
    res, bindir, homedir = run_upgrade(wrkdir=tmp_path)
    assert res.returncode == 0
    assert (bindir / "chromedriver").exists()
    assert os.access(bindir / "chromedriver", os.X_OK)
    assert NEW_VERSION in (bindir / "chromedriver").read_text()


def test_driver_already_up_to_date(tmp_path):
    res, bindir, homedir = run_upgrade(chromedriver=NEW_VERSION, wrkdir=tmp_path, tools=False)
    assert "already installed" in res.stdout
    assert res.returncode == 0


@pytest.mark.parametrize(
    "chromedriver_version",
    [
        pytest.param(OLD_VERSION, id="Old driver is present"),
        pytest.param(None, id="No driver is present"),
    ],
)
def test_target_dir_change(tmp_path, chromedriver_version):
    tgt_dir = tmp_path / "target"
    tgt_dir.mkdir()
    res, bindir, homedir = run_upgrade(
        args=["--target-dir", str(tgt_dir)], chromedriver=chromedriver_version, wrkdir=tmp_path
    )
    assert (tgt_dir / "chromedriver").exists()
    assert os.access(tgt_dir / "chromedriver", os.X_OK)
    assert res.returncode == 0


def test_dry_run(tmp_path):
    res, bindir, homedir = run_upgrade(args=["--dry"], wrkdir=tmp_path)
    assert "Found downloadable chromedriver" in res.stdout
    assert OLD_VERSION in (bindir / "chromedriver").read_text()
    assert res.returncode == 0


def test_force_install(tmp_path):  # force reinstall
    res, bindir, homedir = run_upgrade(args=["--force"], chrome=OLD_VERSION, chromedriver=OLD_VERSION, wrkdir=tmp_path)
    assert "example.com" in (bindir / "chromedriver").read_text()  # Ensure downloading happened
    assert res.returncode == 0


def test_download_dir_change(tmp_path):
    dl_dir = tmp_path / "downloads"
    dl_dir.mkdir()
    res, bindir, homedir = run_upgrade(
        args=["--leave-zip-on-failure", "--download-dir", str(dl_dir)],
        chromedriver=False,
        wrkdir=tmp_path,
        unzip_success=False,
    )
    assert sum(1 for _ in dl_dir.iterdir()) == 1
    assert res.returncode == 1


def test_platform_specified(tmp_path):
    res, bindir, homedir = run_upgrade(args=["--platform", "win64", "--dry"], chromedriver=False, wrkdir=tmp_path)
    assert "Found downloadable chromedriver" in res.stdout
    assert "/win64/" in res.stdout
    assert res.returncode == 0


@pytest.mark.parametrize(
    ["args", "source"],
    [
        pytest.param(["--chrome", NEW_VERSION], "Command line", id="Commmand line with --chrome"),
        pytest.param([NEW_VERSION], "Command line", id="As positional argument"),
        pytest.param(["--apt"], "APT cache", id="Version from APT cache"),
    ],
)
def test_version_from_various_sources(tmp_path, args, source):
    res, bindir, homedir = run_upgrade(args=args, chrome=False, chromedriver=False, wrkdir=tmp_path)
    assert "Found downloadable chromedriver" in res.stdout
    assert source in res.stdout


def test_download_only(tmp_path):
    tgt_dir = tmp_path / "target"
    tgt_dir.mkdir()
    dl_dir = tmp_path / "downloads"
    dl_dir.mkdir()
    res, bindir, homedir = run_upgrade(
        args=["--download-only", "--target-dir", str(tgt_dir), "--download-dir", str(dl_dir)],
        chromedriver=False,
        wrkdir=tmp_path,
    )
    assert res.returncode == 0
    assert not (tgt_dir / "chromedriver").exists()
    assert sum(1 for _ in dl_dir.iterdir()) == 1
    assert next(iter(dl_dir.iterdir())).name.startswith(f"chromedriver-linux64-{NEW_VERSION}")


def test_help_flag(tmp_path):
    res, bindir, homedir = run_upgrade(args=["--help"], wrkdir=tmp_path)
    assert "Usage:" in res.stdout
    assert res.returncode == 1


# === NEGATIVE PATHS ===


def test_missing_tools(tmp_path):  # no curl/jq/unzip
    res, bindir, homedir = run_upgrade(tools=False, wrkdir=tmp_path)
    assert res.returncode != 0
    assert "Required tool" in res.stdout


@pytest.mark.parametrize(
    ["curl_success", "curl_download"],
    [
        pytest.param(False, False, id="curl returns error"),
        pytest.param(True, False, id="curl does not create a file"),
    ],
)
def test_curl_fail(tmp_path, curl_success, curl_download):
    res, bindir, homedir = run_upgrade(
        curl_success=curl_success, curl_download=curl_download, chromedriver=False, wrkdir=tmp_path
    )
    assert res.returncode != 0
    assert "Failed to download" in res.stdout


@pytest.mark.parametrize(
    ["verify", "unzip", "message"],
    [
        pytest.param(False, True, "Failed to download", id="Fail on verification"),
        pytest.param(True, False, "Failed to extract", id="Fail on extraction"),
    ],
)
def test_unzip_fail(tmp_path, verify, unzip, message):
    res, bindir, homedir = run_upgrade(unzip_verify=verify, unzip_success=unzip, chromedriver=False, wrkdir=tmp_path)
    assert res.returncode != 0
    assert message in res.stdout


def test_no_chrome(tmp_path):
    res, bindir, homedir = run_upgrade(update_found=False, chrome=False, wrkdir=tmp_path)
    assert res.returncode != 0
    assert "Google Chrome is not installed" in res.stdout


def test_no_driver_version_available(tmp_path):
    res, bindir, homedir = run_upgrade(update_found=False, chromedriver=False, wrkdir=tmp_path)
    assert res.returncode != 0
    assert "Could not find downloadable chromedriver" in res.stdout


def test_apt_version_not_found(tmp_path):
    res, bindir, homedir = run_upgrade(args=["--apt"], apt_version=None, chromedriver=False, wrkdir=tmp_path)
    assert "No upgradable google-chrome-stable" in res.stdout
    assert res.returncode == 0


def test_download_dir_not_writable(tmp_path):
    dl_dir = tmp_path / "downloads"
    dl_dir.mkdir()
    dl_dir.chmod(0o500)  # Read-only
    res, bindir, homedir = run_upgrade(args=["--download-dir", str(dl_dir)], chromedriver=False, wrkdir=tmp_path)
    assert res.returncode != 0
    assert "Download directory is not writable" in res.stdout
