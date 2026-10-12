"""Publish verified uploads with the correct GitHub Latest/preview designation."""

import argparse
import json
import re
import subprocess

REPO = "rages4calm/earthbound-companion"
TAG = re.compile(r"v(\d+)\.(\d+)\.(\d+)-(redux-dev|ports-preview)\.(\d+)")


def gh(*args):
    result = subprocess.run(
        ["gh", *args], check=True, capture_output=True, text=True, encoding="utf-8"
    )
    return result.stdout


def identity(tag):
    match = TAG.fullmatch(tag)
    if match is None:
        raise ValueError(f"Unsupported release tag: {tag}")
    major, minor, patch, kind, revision = match.groups()
    return kind, tuple(map(int, (major, minor, patch, revision)))


def publish(tag, check_only=False):
    kind, version = identity(tag)
    pages = json.loads(gh("api", "--paginate", "--slurp", f"repos/{REPO}/releases"))
    releases = [release for page in pages for release in page]
    target = next(release for release in releases if release["tag_name"] == tag)
    if not target["assets"] or any(
        asset["state"] != "uploaded" or asset["size"] <= 0
        for asset in target["assets"]
    ):
        raise ValueError("Release has no completed package uploads")

    published = []
    for release in releases:
        if release["draft"] or TAG.fullmatch(release["tag_name"]) is None:
            continue
        release_kind, release_version = identity(release["tag_name"])
        published.append((release_kind, release_version, release["tag_name"]))
    if any(k == kind and v > version for k, v, _ in published):
        raise ValueError("Refusing to publish/check an older release as current")

    windows = [(v, t) for k, v, t in published if k == "redux-dev"]
    if kind == "redux-dev":
        windows.append((version, tag))
    expected_latest = max(windows)[1]
    if not check_only:
        gh(
            "release", "edit", tag, "--repo", REPO, "--draft=false",
            f"--prerelease={'true' if kind == 'ports-preview' else 'false'}",
            f"--latest={'true' if kind == 'redux-dev' else 'false'}",
        )

    actual = json.loads(gh("api", f"repos/{REPO}/releases/tags/{tag}"))
    latest = json.loads(gh("api", f"repos/{REPO}/releases/latest"))
    if actual["draft"] or actual["prerelease"] != (kind == "ports-preview"):
        raise ValueError("Published release has the wrong draft/prerelease status")
    if latest["tag_name"] != expected_latest:
        raise ValueError(f"Latest is {latest['tag_name']}, expected {expected_latest}")
    return {"tag": tag, "prerelease": actual["prerelease"],
            "latest": latest["tag_name"], "url": actual["html_url"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag", help="Already uploaded and verified release tag")
    parser.add_argument("--check", action="store_true", help="Verify without editing")
    args = parser.parse_args()
    print(json.dumps(publish(args.tag, args.check), indent=2))
