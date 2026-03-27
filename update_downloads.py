#!/usr/bin/env python3
"""Fetches total PyPI downloads for all packages and updates README.md."""

import re
import urllib.request
import json

PACKAGES = [
    "betterpassphrase",
    "datasetpipeline",
    "jsondbin",
    "smart-commit-ai",
    "creatree",
    "sqlstream",
]


def get_total_downloads(package: str) -> int:
    """Fetch total downloads from PePy API (no auth needed for basic stats)."""
    url = f"https://pepy.tech/api/v2/projects/{package}"
    req = urllib.request.Request(url, headers={"User-Agent": "readme-updater/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            return data.get("total_downloads", 0)
    except Exception:
        pass

    # Fallback: parse the badge SVG for the number
    badge_url = f"https://static.pepy.tech/badge/{package}"
    req = urllib.request.Request(badge_url, headers={"User-Agent": "readme-updater/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            svg = resp.read().decode()
            # Badge SVGs contain text like "12.3k" or "1,234"
            matches = re.findall(r">(\d[\d,.]*[kKmM]?)<", svg)
            if matches:
                return parse_badge_number(matches[-1])
    except Exception:
        pass

    return 0


def parse_badge_number(s: str) -> int:
    """Parse badge display numbers like '12.3k' or '1,234' into integers."""
    s = s.strip().replace(",", "")
    if s.lower().endswith("k"):
        return int(float(s[:-1]) * 1000)
    if s.lower().endswith("m"):
        return int(float(s[:-1]) * 1000000)
    return int(float(s))


def format_downloads(total: int) -> str:
    """Format total into a human-readable string like '43,000+' or '125k+'."""
    if total >= 1_000_000:
        return f"{total / 1_000_000:.1f}M+"
    if total >= 100_000:
        return f"{total // 1000}k+"
    if total >= 10_000:
        # Round down to nearest thousand
        rounded = (total // 1000) * 1000
        return f"{rounded:,}+"
    return f"{total:,}+"


def main():
    total = 0
    for pkg in PACKAGES:
        count = get_total_downloads(pkg)
        print(f"  {pkg}: {count:,}")
        total += count

    formatted = format_downloads(total)
    print(f"\n  Total: {total:,} → displaying as: {formatted}")

    # Update README.md
    with open("README.md", "r") as f:
        content = f.read()

    pattern = r"<!-- DOWNLOADS_START -->.*?<!-- DOWNLOADS_END -->"
    replacement = f"<!-- DOWNLOADS_START -->{formatted}<!-- DOWNLOADS_END -->"

    new_content, count = re.subn(pattern, replacement, content)

    if count == 0:
        print("\n  ⚠ No DOWNLOADS markers found in README.md")
        return

    if new_content == content:
        print("\n  ✓ No change needed")
        return

    with open("README.md", "w") as f:
        f.write(new_content)

    print(f"\n  ✓ Updated README.md with {formatted}")


if __name__ == "__main__":
    main()
