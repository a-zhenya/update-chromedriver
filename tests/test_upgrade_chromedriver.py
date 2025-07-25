import subprocess as sp
from pathlib import Path
import os

OLD_VERSION = "1.1.1.1"
NEW_VERSION = "2.2.2.2"


def install_chrome(version, path):
    (path / "google-chrome").write_text(f"#!/bin/bash\necho Google Chrome {version}\n")
    (path / "google-chrome").chmod(0o755)


def install_chromedriver(version, path):
    (path / "chromedriver").write_text(f"#!/bin/bash\necho ChromeDriver {version} '(hash)'\n")
    (path / "chromedriver").chmod(0o755)


def install_curl(success, path):
    script = (
        """#!/bin/bash
while [ $# -gt 0 ]; do
    if [ "$1" = "-o" ]; then shift; FILE="$1"; fi
    shift
done
if [ -n "$FILE" ]; then
    touch "$FILE"
fi
"""
        if success
        else "#!/bin/bash\nexit 1\n"
    )
    (path / "curl").write_text(script)
    (path / "curl").chmod(0o755)


def install_jq(success, path):
    script = "echo http://example.com/downloads/chromedriver.zip" if success else ""
    (path / "jq").write_text(f"#!/bin/bash\n{script}\n")
    (path / "jq").chmod(0o755)


def install_unzip(success, path):
    script = (
        """#!/bin/bash
while [ $# -gt 0 ]; do
    if [ "$1" = "-d" ]; then shift; DIR="$1"; fi
    shift
done
touch "$DIR/chromedriver"
"""
        if success
        else "#!/bin/bash\nexit 1\n"
    )
    (path / "unzip").write_text(script)
    (path / "unzip").chmod(0o755)


def mock_apt(version, path):
    out = f'echo "Conf google-chrome-stable: {version}"' if version else ""
    (path / "apt-get").write_text(f"#!/bin/bash\n{out}\n")
    (path / "apt-get").chmod(0o755)


def run_upgrade(
    args=None,
    env=None,
    chrome=NEW_VERSION,
    chromedriver=OLD_VERSION,
    tools=True,
    update_found=True,
    curl_success=True,
    apt_version=NEW_VERSION,
    unzip_success=True,
    wrkdir=".",
):
    args = ["bash", "upgrade-chromedriver"] + (args or [])
    bindir = Path(wrkdir) / "bin"
    bindir.mkdir(exist_ok=True)
    for tool in ["bash", "cat", "grep", "chmod", "cut", "touch", "rm", "ls", "dirname"]:
        os.symlink(f"/bin/{tool}", bindir / tool)
    if chrome:
        install_chrome(chrome, bindir)
    if chromedriver:
        install_chromedriver(chromedriver, bindir)
    if tools:
        install_curl(curl_success, bindir)
        install_jq(update_found, bindir)
        install_unzip(unzip_success, bindir)
    mock_apt(apt_version, bindir)

    homedir = Path(wrkdir) / "home"
    (homedir / ".local" / "bin").mkdir(parents=True, exist_ok=True)
    env = env or {}
    env.update({"HOME": str(homedir), "PATH": str(bindir)})
    return sp.run(args, text=True, stdin=sp.DEVNULL, stdout=sp.PIPE, stderr=sp.PIPE, env=env), bindir, homedir


# === POSITIVE PATHS ===


def test_replace_driver(tmp_path):  # default upgrade
    res, bindir, homedir = run_upgrade(wrkdir=tmp_path)
    assert res.returncode == 0
    assert (bindir / "chromedriver").exists()


def test_driver_already_up_to_date(tmp_path):  # no need to upgrade
    res, bindir, homedir = run_upgrade(chromedriver=NEW_VERSION, wrkdir=tmp_path, tools=False)
    assert "already installed" in res.stdout
    assert res.returncode == 0


def test_new_driver(tmp_path):  # no chromedriver before
    res, bindir, homedir = run_upgrade(chromedriver=False, wrkdir=tmp_path)
    assert (homedir / ".local" / "bin" / "chromedriver").exists(), "Xxxx\n" + res.stdout
    assert res.returncode == 0


def test_target_dir_change(tmp_path):  # custom target
    tgt_dir = tmp_path / "target"
    tgt_dir.mkdir()
    res, bindir, homedir = run_upgrade(args=["--target-dir", str(tgt_dir)], chromedriver=False, wrkdir=tmp_path)
    assert (tgt_dir / "chromedriver").exists()
    assert res.returncode == 0


def test_dry_run(tmp_path):  # dry
    res, bindir, homedir = run_upgrade(args=["--dry"], wrkdir=tmp_path)
    assert "Found downloadable chromedriver" in res.stdout
    assert res.returncode == 0


def test_force_install(tmp_path):  # force reinstall
    res, bindir, homedir = run_upgrade(args=["--force"], wrkdir=tmp_path)
    assert res.returncode == 0


def test_download_dir_change(tmp_path):  # custom download dir
    dl_dir = tmp_path / "downloads"
    dl_dir.mkdir()
    res, bindir, homedir = run_upgrade(
        args=["--leave-zip-on-failure", "--download-dir", str(dl_dir)],
        chromedriver=False,
        wrkdir=tmp_path,
        unzip_success=False,
    )
    assert len(list(dl_dir.iterdir())) == 1
    assert res.returncode == 1


def test_platform_specified(tmp_path):  # platform specified
    res, bindir, homedir = run_upgrade(args=["--platform", "win64"], chromedriver=False, wrkdir=tmp_path)
    assert res.returncode == 0


def test_cli_version(tmp_path):  # -v version
    res, bindir, homedir = run_upgrade(args=["-v", NEW_VERSION], chrome=False, chromedriver=False, wrkdir=tmp_path)
    assert "Found downloadable chromedriver" in res.stdout


def test_version_without_flag(tmp_path):  # bare version
    res, bindir, homedir = run_upgrade(args=[NEW_VERSION], chrome=False, chromedriver=False, wrkdir=tmp_path)
    assert "Found downloadable chromedriver" in res.stdout


def test_version_from_apt(tmp_path):
    res, bindir, homedir = run_upgrade(args=["--apt"], chrome=False, chromedriver=False, wrkdir=tmp_path)
    assert "APT cache" in res.stdout


# === NEGATIVE PATHS ===


def test_missing_tools(tmp_path):  # no curl/jq/unzip
    res, bindir, homedir = run_upgrade(tools=False, wrkdir=tmp_path)
    assert res.returncode != 0
    assert "Required tool" in res.stdout


def test_download_fail(tmp_path):
    res, bindir, homedir = run_upgrade(curl_success=False, chromedriver=False, wrkdir=tmp_path)
    assert res.returncode != 0
    assert "Failed to download" in res.stdout


def test_unzip_fail(tmp_path):
    res, bindir, homedir = run_upgrade(unzip_success=False, chromedriver=False, wrkdir=tmp_path)
    assert res.returncode != 0
    assert "Failed to extract" in res.stdout


def test_invalid_api_response(tmp_path):
    res, bindir, homedir = run_upgrade(update_found=False, chromedriver=False, wrkdir=tmp_path)
    assert res.returncode != 0
    assert "Could not find downloadable chromedriver" in res.stdout


def test_apt_version_not_found(tmp_path):
    res, bindir, homedir = run_upgrade(args=["--apt"], apt_version=None, chromedriver=False, wrkdir=tmp_path)
    assert "Cannot find the upgradable" in res.stdout
    assert res.returncode == 0


def test_download_only(tmp_path):
    tgt_dir = tmp_path / "target"
    tgt_dir.mkdir()
    res, bindir, homedir = run_upgrade(args=["--download-only", "--target-dir", str(tgt_dir)], chromedriver=False, wrkdir=tmp_path)
    assert res.returncode == 0
    assert not (tgt_dir / "chromedriver").exists()


def test_help_flag(tmp_path):
    res, bindir, homedir = run_upgrade(args=["--help"], wrkdir=tmp_path)
    assert "Usage:" in res.stdout
    assert res.returncode == 1
