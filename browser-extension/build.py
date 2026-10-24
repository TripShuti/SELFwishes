#!/usr/bin/env python3
"""Build unpacked and ZIP packages without external tools or remote code."""
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT.parent / "frontend/public/extensions"
BASE = {
    "manifest_version": 3,
    "name": "SELFwishes Browser Connector",
    "version": "1.0.1",
    "description": "Connect your signed-in HoYoverse account to your own SELFwishes server.",
    "permissions": ["activeTab", "cookies", "scripting", "storage"],
    "host_permissions": ["https://*.hoyoverse.com/*", "https://*.hoyolab.com/*"],
    "optional_host_permissions": ["http://*/*", "https://*/*"],
    "action": {"default_title": "Connect SELFwishes"},
}


def build():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for browser in ("chromium", "firefox"):
        target = ROOT / "dist" / browser
        target.mkdir(parents=True, exist_ok=True)
        for source in (ROOT / "shared").iterdir():
            shutil.copyfile(source, target / source.name)
        manifest = {**BASE}
        if browser == "chromium":
            manifest["background"] = {"service_worker": "background.js"}
        else:
            manifest["background"] = {"scripts": ["background.js"]}
            manifest["browser_specific_settings"] = {"gecko": {
                "id": "selfwishes-connector@selfwishes.local", "strict_min_version": "142.0",
                "data_collection_permissions": {"required": ["authenticationInfo"], "optional": []},
            }}
        (target / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        archive = OUTPUT / f"selfwishes-{browser}.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
            for source in sorted(target.iterdir()):
                bundle.write(source, source.name)
        print(archive)


if __name__ == "__main__":
    build()
