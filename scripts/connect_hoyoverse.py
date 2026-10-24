#!/usr/bin/env python3
"""Run on the computer with LibreWolf; sends only HoYoverse cookies over SSH."""
import argparse
import configparser
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile

COOKIE_NAMES = ("account_id_v2", "account_mid_v2", "cookie_token_v2")


def find_profile() -> Path:
    for root in (Path.home() / ".config/librewolf/librewolf", Path.home() / ".librewolf",
                 Path.home() / ".var/app/io.gitlab.librewolf-community/.librewolf"):
        ini = root / "profiles.ini"
        if not ini.exists():
            continue
        config = configparser.ConfigParser()
        config.read(ini)
        for section in config.sections():
            default = config[section].get("Default", "")
            if section.startswith("Install") and default:
                path = root / default / "cookies.sqlite"
                if path.is_file():
                    return path
        profiles = [s for s in config.sections() if s.startswith("Profile")]
        profiles.sort(key=lambda s: config[s].get("Default") != "1")
        for section in profiles:
            profile = Path(config[section]["Path"])
            if config[section].get("IsRelative", "1") == "1":
                profile = root / profile
            if (profile / "cookies.sqlite").is_file():
                return profile / "cookies.sqlite"
    raise RuntimeError("LibreWolf profile not found. Pass --profile /path/to/profile.")


def read_cookies(database: Path) -> dict:
    # Private temporary directory, deleted immediately after reading. Copy WAL too
    # because LibreWolf may be running and holding an exclusive database lock.
    with tempfile.TemporaryDirectory(prefix="selfwishes-hoyo-") as directory:
        target = Path(directory) / "cookies.sqlite"
        for suffix in ("", "-wal", "-shm"):
            source = Path(str(database) + suffix)
            if source.exists():
                shutil.copyfile(source, Path(str(target) + suffix))
        with sqlite3.connect(target) as db:
            rows = db.execute("SELECT host,name,value FROM moz_cookies "
                              "WHERE host IN ('.hoyoverse.com','.hoyolab.com') "
                              "AND name IN (?,?,?) AND originAttributes=''", COOKIE_NAMES).fetchall()
        # Do not combine cookies from different domains/accounts.
        for domain in (".hoyoverse.com", ".hoyolab.com"):
            cookies = {name: value for host, name, value in rows if host == domain}
            if all(cookies.get(name) for name in COOKIE_NAMES):
                return cookies
    raise RuntimeError("Required cookies not found. Sign in to HoYoverse in LibreWolf first.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", default="trip@192.168.1.110")
    parser.add_argument("--profile", type=Path, help="LibreWolf profile directory")
    args = parser.parse_args()
    database = args.profile / "cookies.sqlite" if args.profile else find_profile()
    cookies = read_cookies(database)
    result = subprocess.run(["ssh", "-o", "ConnectTimeout=10", "--", args.server,
                             "docker exec -i selfwishes python -m app.connect_hoyo"],
                            input=json.dumps(cookies).encode(), check=False)
    if result.returncode:
        raise RuntimeError("Connection failed. Check SSH access and HoYoverse login.")
    print("Open SELFwishes and click Update history. No scheduled updates are enabled.")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, sqlite3.Error, configparser.Error) as exc:
        # Never print database contents, cookies, or request exceptions.
        print(str(exc) if isinstance(exc, RuntimeError) else "Could not read LibreWolf or run SSH.", file=sys.stderr)
        sys.exit(1)
