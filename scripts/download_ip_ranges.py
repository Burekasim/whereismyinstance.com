#!/usr/bin/env python3
"""
Download the latest IP range files for all supported cloud providers.
Writes files into <repo_root>/lambda/json/.

Usage:
    python scripts/download_ip_ranges.py
"""

import csv
import ipaddress
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

OUT_DIR = Path(__file__).parent.parent / "lambda" / "json"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def fetch(url: str, *, text=False) -> bytes | str:
    print(f"  GET {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "whereismyinstance/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    return data.decode() if text else data


def save(name: str, data: bytes | str):
    path = OUT_DIR / name
    if isinstance(data, str):
        data = data.encode()
    path.write_bytes(data)
    print(f"  Saved {path} ({len(data):,} bytes)")


# ── AWS ───────────────────────────────────────────────────
def download_aws():
    print("AWS...")
    save("aws_ranges.json", fetch("https://ip-ranges.amazonaws.com/ip-ranges.json"))


# ── GCP ───────────────────────────────────────────────────
def download_gcp():
    print("GCP...")
    save("gcp_ranges.json", fetch("https://www.gstatic.com/ipranges/cloud.json"))


# ── Oracle ────────────────────────────────────────────────
def download_oracle():
    print("Oracle...")
    save(
        "oracle_ranges.json",
        fetch("https://docs.oracle.com/en-us/iaas/tools/public_ip_ranges.json"),
    )


# ── Azure ─────────────────────────────────────────────────
def download_azure():
    """
    Azure's download URL is a rotating GUID link on the download page.
    We scrape the page to find the current direct URL.
    """
    print("Azure (scraping download page)...")
    page = fetch(
        "https://www.microsoft.com/en-us/download/details.aspx?id=56519", text=True
    )
    # The JSON download link looks like:
    # https://download.microsoft.com/download/.../ServiceTags_Public_YYYYMMDD.json
    match = re.search(
        r'https://download\.microsoft\.com/download/[^"\']+ServiceTags_Public_\d+\.json',
        page,
    )
    if not match:
        # Fallback: try the confirmation page pattern
        match = re.search(
            r'"(https://download\.microsoft\.com/download/[^"]+\.json)"', page
        )
    if not match:
        print("  WARNING: could not find Azure download URL, skipping.")
        return
    url = match.group(0).strip('"')
    save("azure_ranges.json", fetch(url))


# ── Cloudflare ────────────────────────────────────────────
def download_cloudflare():
    """
    Cloudflare publishes separate IPv4 and IPv6 lists.
    We combine them into one newline-delimited file.
    """
    print("Cloudflare...")
    ipv4 = fetch("https://www.cloudflare.com/ips-v4", text=True).strip()
    ipv6 = fetch("https://www.cloudflare.com/ips-v6", text=True).strip()
    combined = "\n".join(filter(None, [ipv4, ipv6]))
    save("cloudflare_ranges.json", combined)  # kept as .json for compat with Lambda


# ── DigitalOcean ──────────────────────────────────────────
def download_digitalocean():
    print("DigitalOcean...")
    save(
        "digitalocean_ranges.csv",
        fetch("https://digitalocean.com/geo/google.csv"),
    )


# ── Main ──────────────────────────────────────────────────
DOWNLOADERS = [
    download_aws,
    download_gcp,
    download_oracle,
    download_azure,
    download_cloudflare,
    download_digitalocean,
]

def _ipv4_count(cidr: str) -> int:
    try:
        net = ipaddress.ip_network(cidr, strict=False)
        return net.num_addresses if net.version == 4 else 0
    except Exception:
        return 0


def write_stats(downloaded_at: str):
    """Compute IP counts per provider and write stats.json next to the range files."""
    print("Computing stats...")
    providers = {}

    # AWS
    try:
        d = json.loads((OUT_DIR / "aws_ranges.json").read_text())
        raw = d.get("createDate", "")
        try:
            from datetime import datetime, timezone
            dt = datetime.strptime(raw, "%Y-%m-%d-%H-%M-%S").replace(tzinfo=timezone.utc)
            updated = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            updated = downloaded_at
        providers["aws"] = {
            "ip_count": sum(_ipv4_count(p["ip_prefix"]) for p in d.get("prefixes", [])),
            "updated": updated,
        }
    except Exception as e:
        print(f"  stats AWS error: {e}")

    # GCP
    try:
        d = json.loads((OUT_DIR / "gcp_ranges.json").read_text())
        providers["gcp"] = {
            "ip_count": sum(_ipv4_count(p["ipv4Prefix"]) for p in d.get("prefixes", []) if "ipv4Prefix" in p),
            "updated": downloaded_at,
        }
    except Exception as e:
        print(f"  stats GCP error: {e}")

    # Oracle
    try:
        d = json.loads((OUT_DIR / "oracle_ranges.json").read_text())
        providers["oracle"] = {
            "ip_count": sum(_ipv4_count(c["cidr"]) for r in d.get("regions", []) for c in r["cidrs"]),
            "updated": downloaded_at,
        }
    except Exception as e:
        print(f"  stats Oracle error: {e}")

    # Azure
    try:
        d = json.loads((OUT_DIR / "azure_ranges.json").read_text())
        providers["azure"] = {
            "ip_count": sum(
                _ipv4_count(cidr)
                for v in d.get("values", [])
                for cidr in v["properties"]["addressPrefixes"]
            ),
            "updated": downloaded_at,
        }
    except Exception as e:
        print(f"  stats Azure error: {e}")

    # Cloudflare
    try:
        lines = (OUT_DIR / "cloudflare_ranges.json").read_text().splitlines()
        providers["cloudflare"] = {
            "ip_count": sum(_ipv4_count(l.strip()) for l in lines if l.strip()),
            "updated": downloaded_at,
        }
    except Exception as e:
        print(f"  stats Cloudflare error: {e}")

    # DigitalOcean
    try:
        rows = list(csv.reader((OUT_DIR / "digitalocean_ranges.csv").read_text().splitlines()))
        providers["digitalocean"] = {
            "ip_count": sum(_ipv4_count(r[0]) for r in rows if r),
            "updated": downloaded_at,
        }
    except Exception as e:
        print(f"  stats DigitalOcean error: {e}")

    stats = {"providers": providers, "last_updated": downloaded_at}
    path = OUT_DIR / "stats.json"
    path.write_text(json.dumps(stats, indent=2))
    print(f"  Wrote {path}")


def write_metadata():
    """Record the UTC timestamp of this download run."""
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    meta = {"downloaded_at": ts}
    path = OUT_DIR / "metadata.json"
    path.write_text(json.dumps(meta))
    print(f"  Wrote {path} (downloaded_at={ts})")
    return ts


if __name__ == "__main__":
    errors = []
    for fn in DOWNLOADERS:
        try:
            fn()
        except Exception as exc:
            print(f"  ERROR in {fn.__name__}: {exc}", file=sys.stderr)
            errors.append(fn.__name__)

    ts = write_metadata()
    write_stats(ts)

    if errors:
        print(f"\nFailed: {', '.join(errors)}", file=sys.stderr)
        sys.exit(1)
    else:
        print("\nAll IP range files downloaded successfully.")
