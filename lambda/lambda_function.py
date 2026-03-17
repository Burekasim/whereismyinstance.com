import netaddr
import json
import csv
import os
from datetime import datetime, timezone


# ── CORS headers returned with every response ─────────────
CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json",
}

# Files live next to this module inside the Lambda zip
BASE = os.path.dirname(__file__)


def _json_path(name):
    return os.path.join(BASE, "json", name)


def respond(status, body):
    return {"statusCode": status, "headers": CORS, "body": json.dumps(body, indent=2)}


# ── Region → human-readable location ─────────────────────
def reg2loc(region: str):
    locations = {
        # AWS
        "af-south-1": "Africa (Cape Town)",
        "ap-east-1": "Asia Pacific (Hong Kong)",
        "ap-northeast-1": "Asia Pacific (Tokyo)",
        "ap-northeast-2": "Asia Pacific (Seoul)",
        "ap-northeast-3": "Asia Pacific (Osaka)",
        "ap-south-1": "Asia Pacific (Mumbai)",
        "ap-south-2": "Asia Pacific (Hyderabad)",
        "ap-southeast-1": "Asia Pacific (Singapore)",
        "ap-southeast-2": "Asia Pacific (Sydney)",
        "ap-southeast-3": "Asia Pacific (Jakarta)",
        "ap-southeast-4": "Asia Pacific (Melbourne)",
        "ap-southeast-5": "Asia Pacific (Malaysia)",
        "ca-central-1": "Canada (Central)",
        "ca-west-1": "Canada West (Calgary)",
        "cn-north-1": "China (Beijing)",
        "cn-northwest-1": "China (Ningxia)",
        "eu-central-1": "Europe (Frankfurt)",
        "eu-central-2": "Europe (Zurich)",
        "eu-north-1": "Europe (Stockholm)",
        "eu-south-1": "Europe (Milan)",
        "eu-south-2": "Europe (Spain)",
        "eu-west-1": "Europe (Ireland)",
        "eu-west-2": "Europe (London)",
        "eu-west-3": "Europe (Paris)",
        "il-central-1": "Middle East (Israel)",
        "me-central-1": "Middle East (UAE)",
        "me-south-1": "Middle East (Bahrain)",
        "sa-east-1": "South America (Sao Paulo)",
        "us-east-1": "US East (N. Virginia)",
        "us-east-2": "US East (Ohio)",
        "us-gov-east-1": "Us East (GovCloud)",
        "us-gov-west-1": "Us West (GovCloud)",
        "us-west-1": "US West (N. California)",
        "us-west-2": "US West (Oregon)",
        # GCP
        "africa-south1": "Johannesburg, South Africa",
        "asia-east1": "Changhua County, Taiwan",
        "asia-east2": "Hong Kong",
        "asia-northeast1": "Tokyo, Japan",
        "asia-northeast2": "Osaka, Japan",
        "asia-northeast3": "Seoul, South Korea",
        "asia-south1": "Mumbai, India",
        "asia-south2": "Delhi, India",
        "asia-southeast1": "Jurong West, Singapore",
        "asia-southeast2": "Jakarta, Indonesia",
        "australia-southeast1": "Sydney, Australia",
        "australia-southeast2": "Melbourne, Australia",
        "europe-central2": "Warshaw, Poland",
        "europe-north1": "Hamina, Finland",
        "europe-southwest1": "Madrid, Spain",
        "europe-west1": "St. Ghislain, Belgium",
        "europe-west10": "Berlin, Germany",
        "europe-west12": "Turin, Italy",
        "europe-west2": "London, England",
        "europe-west3": "Frankfurt, Germany",
        "europe-west4": "Eemshaven, Netherlands",
        "europe-west6": "Zurich, Switzerland",
        "europe-west8": "Milan, Italy",
        "europe-west9": "Paris, France",
        "me-central1": "Doha, Qatar",
        "me-central2": "Dammam, Saudi Arabia",
        "me-west1": "Tel Aviv, Israel",
        "northamerica-northeast1": "Montreal, Canada",
        "northamerica-northeast2": "Toronto, Canada",
        "southamerica-east1": "Osasco, Sao Paulo, Brazil",
        "southamerica-west1": "Shantiago, Chile",
        "us-central1": "Council Bluffs, Iowa, United States",
        "us-central2": "Mayes County, Oklahoma, United States",
        "us-east1": "Moncks Corner, South Carolina, United States",
        "us-east4": "Ashburn, Virginia, United States",
        "us-east5": "Columbus, Ohio, United States",
        "us-east7": "Jackson County, Alabama, United States",
        "us-south1": "Dallas, Texas, United States",
        "us-west1": "The Dalles, Oregon, United States",
        "us-west2": "Los Angeles, California, United States",
        "us-west3": "Salt Lake City, Utah, United States",
        "us-west4": "Las Vegas, Nevada, United States",
        # Oracle
        "af-johannesburg-1": "South Africa Central (Johannesburg)",
        "eu-milan-1": "Italy Northwest (Milan)",
        "eu-paris-1": "France Central (Paris)",
        "eu-stockholm-1": "Sweden Central (Stockholm)",
        "mx-queretaro-1": "Mexico Central (Queretaro)",
        "ap-chuncheon-1": "South Korea North (Chuncheon)",
        "ap-hyderabad-1": "India South (Hyderabad)",
        "ap-melbourne-1": "Australia Southeast (Melbourne)",
        "ap-mumbai-1": "India West (Mumbai)",
        "ap-osaka-1": "Japan Central (Osaka)",
        "ap-seoul-1": "South Korea Central (Seoul)",
        "ap-singapore-1": "Singapore (Singapore)",
        "ap-sydney-1": "Australia East (Sydney)",
        "ap-tokyo-1": "Japan East (Tokyo)",
        "ca-montreal-1": "Canada Southeast (Montreal)",
        "ca-toronto-1": "Canada Southeast (Toronto)",
        "eu-amsterdam-1": "Netherlands Northwest (Amsterdam)",
        "eu-frankfurt-1": "Germany Central (Frankfurt)",
        "eu-marseille-1": "France South (Marseille)",
        "eu-zurich-1": "Switzerland North (Zurich)",
        "il-jerusalem-1": "Israel Central (Jerusalem)",
        "me-abudhabi-1": "UAE Central (Abu Dhabi)",
        "me-dubai-1": "UAE East (Dubai)",
        "me-jeddah-1": "Saudi Arabia West (Jeddah)",
        "sa-santiago-1": "Chile (Santiago)",
        "sa-saopaulo-1": "Brazil East (Sao Paulo)",
        "sa-vinhedo-1": "Brazil Southeast (Vinhedo)",
        "uk-cardiff-1": "UK West (Newport)",
        "uk-london-1": "UK South (London)",
        "us-ashburn-1": "US East (Ashburn)",
        "us-phoenix-1": "US West (Phoenix)",
        "us-sanjose-1": "US West (San Jose)",
        # Azure
        "australiacentral2": "Central 2",
        "australiacentral": "Australia Central",
        "australiaeast": "Australia East",
        "australiasoutheast": "Australia Southeast",
        "brazilsouth": "Brazil South",
        "brazilsoutheast": "Brazil Southeast",
        "canadacentral": "Canada Central",
        "canadaeast": "Canada East",
        "centralindia": "Central India",
        "centralus": "Central US",
        "eastasia": "East Asia",
        "eastus2": "US 2",
        "eastus": "East US",
        "francecentral": "France Central",
        "francesouth": "France South",
        "germanynorth": "Germany North",
        "germanywestcentral": "West Central",
        "japaneast": "Japan East",
        "japanwest": "Japan West",
        "jioindiacentral": "Central India",
        "jioindiawest": "West India",
        "koreacentral": "Korea Central",
        "koreasouth": "Korea South",
        "northcentralus": "Central US",
        "northeurope": "North Europe",
        "norwayeast": "Norway East",
        "norwaywest": "Norway West",
        "southafricanorth": "Africa North",
        "southafricawest": "Africa West",
        "southcentralus": "Central US",
        "southeastasia": "Southeast Asia",
        "southindia": "South India",
        "swedencentral": "Central Sweden",
        "switzerlandnorth": "Switzerland North",
        "switzerlandwest": "Switzerland West",
        "uaecentral": "UAE Central",
        "uaenorth": "UAE North",
        "uksouth": "UK South",
        "ukwest": "UK West",
        "westcentralus": "Central US",
        "westeurope": "West Europe",
        "westindia": "West India",
        "westus2": "West US",
        "westus3": "West US",
        "westus": "West US",
        # DigitalOcean
        "amsterdam_1098_xh": "Amsterdam, 1098 XH, The Netherlands",
        "bangalore_560100": "Bangalore, 560100, India",
        "clifton_07014": "Clifton, 07014, New Jersey, United States",
        "douglasville_30122": "Douglasville, 30122, Georgia, United States",
        "frankfurt_60341": "Frankfurt, 60341, Germany",
        "london_sl1_4ax": "London, SL1 4AX, United Kingdom",
        "north_bergen_07047": "North Bergen, 07047, New Jersey, United States",
        "san_francisco_94124": "San Francisco, 94124, United States",
        "santa_clara_95051": "Santa Clara, 95051, California, United States",
        "santa_clara_95054": "Santa Clara, 95054, California, United States",
        "secaucus_07094": "Secaucus, 07094, New Jersey, United States",
        "singapore_627753": "Singapore, 627753, Singapore",
        "sydney_2015": "Sydney, 2015, Australia",
        "toronto_m5a_0b2": "Toronto, M5A 0B2, Canada",
    }
    return locations.get(region)


# ── Provider lookup functions ─────────────────────────────

def aws_ranges(ip: str):
    with open(_json_path("aws_ranges.json")) as f:
        data = json.load(f)
    services = []
    ip_range = region = region_location = None
    for p in data["prefixes"]:
        if netaddr.IPAddress(ip) in netaddr.IPNetwork(p["ip_prefix"]):
            ip_range = p["ip_prefix"]
            region = p["region"]
            region_location = reg2loc(region)
            services.append(p["service"])
    if not services:
        return respond(404, {"results": "No matches found"})
    return respond(200, {
        "cloud": "Amazon Web Services",
        "ip_range": ip_range,
        "region": region,
        "region_location": region_location,
        "service": services,
    })


def gcp_ranges(ip: str):
    with open(_json_path("gcp_ranges.json")) as f:
        data = json.load(f)
    for p in data["prefixes"]:
        if "ipv4Prefix" in p:
            if netaddr.IPAddress(ip) in netaddr.IPNetwork(p["ipv4Prefix"]):
                return respond(200, {
                    "cloud": "Google Cloud Platform",
                    "ip_range": p["ipv4Prefix"],
                    "region": p["scope"],
                    "region_location": reg2loc(p["scope"]),
                    "service": [p["service"]],
                })
    return respond(404, {"results": "No matches found"})


def oracle_ranges(ip):
    with open(_json_path("oracle_ranges.json")) as f:
        data = json.load(f)
    for region_entry in data["regions"]:
        for cidr_entry in region_entry["cidrs"]:
            if netaddr.IPAddress(ip) in netaddr.IPNetwork(cidr_entry["cidr"]):
                return respond(200, {
                    "cloud": "Oracle Cloud",
                    "ip_range": cidr_entry["cidr"],
                    "region": region_entry["region"],
                    "region_location": reg2loc(region_entry["region"]),
                    "service": cidr_entry["tags"],
                })
    return respond(404, {"results": "No matches found"})


def azure_ranges(ip):
    with open(_json_path("azure_ranges.json")) as f:
        data = json.load(f)
    for resource in data["values"]:
        for cidr in resource["properties"]["addressPrefixes"]:
            if netaddr.IPAddress(ip) in netaddr.IPNetwork(cidr):
                region = resource["properties"]["region"]
                if not region:
                    continue
                return respond(200, {
                    "cloud": "Microsoft Azure",
                    "ip_range": cidr,
                    "region": region,
                    "region_location": reg2loc(region),
                    "service": [resource["id"]],
                })
    return respond(404, {"results": "No matches found"})


def cloudflare_ranges(ip):
    with open(_json_path("cloudflare_ranges.json")) as f:
        cidrs = [line.strip() for line in f if line.strip()]
    for cidr in cidrs:
        if netaddr.IPAddress(ip) in netaddr.IPNetwork(cidr):
            return respond(200, {
                "cloud": "CloudFlare",
                "ip_range": cidr,
                "region": "Global",
                "region_location": "Global",
                "service": "CloudFlare WAF/CDN",
            })
    return respond(404, {"results": "No matches found"})


def digitalocean_ranges(ip):
    with open(_json_path("digitalocean_ranges.csv")) as f:
        fieldnames = ["cidr", "country", "country-city", "city", "zipcode"]
        for row in csv.DictReader(f, fieldnames=fieldnames):
            if netaddr.IPAddress(ip) in netaddr.IPNetwork(row["cidr"]):
                city_key = row["city"].replace(" ", "_").lower() + "_" + row["zipcode"]
                return respond(200, {
                    "cloud": "DigitalOcean",
                    "ip_range": row["cidr"],
                    "region": row["country"],
                    "region_location": reg2loc(city_key),
                    "service": "DigitalOcean",
                })
    return respond(404, {"results": "No matches found"})


# ── Stats helpers ─────────────────────────────────────────

def _ipv4_size(cidr: str) -> int:
    """Return the number of IPv4 addresses in a CIDR block; 0 for IPv6."""
    try:
        net = netaddr.IPNetwork(cidr)
        return net.size if net.version == 4 else 0
    except Exception:
        return 0


def _file_mtime(name: str) -> str:
    """Return the file's last-modified time as ISO-8601, falling back to now."""
    try:
        ts = os.path.getmtime(_json_path(name))
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── Stats endpoint ────────────────────────────────────────

def get_stats():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    providers = {}

    # AWS — createDate format: "2024-03-01-12-00-00"
    try:
        with open(_json_path("aws_ranges.json")) as f:
            d = json.load(f)
        ip_count = sum(_ipv4_size(p["ip_prefix"]) for p in d.get("prefixes", []))
        raw_date = d.get("createDate", "")
        try:
            dt = datetime.strptime(raw_date, "%Y-%m-%d-%H-%M-%S").replace(tzinfo=timezone.utc)
            updated = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            updated = _file_mtime("aws_ranges.json")
        providers["aws"] = {"ip_count": ip_count, "updated": updated}
    except Exception:
        pass

    # GCP
    try:
        with open(_json_path("gcp_ranges.json")) as f:
            d = json.load(f)
        ip_count = sum(_ipv4_size(p["ipv4Prefix"]) for p in d.get("prefixes", []) if "ipv4Prefix" in p)
        providers["gcp"] = {"ip_count": ip_count, "updated": _file_mtime("gcp_ranges.json")}
    except Exception:
        pass

    # Oracle
    try:
        with open(_json_path("oracle_ranges.json")) as f:
            d = json.load(f)
        ip_count = sum(
            _ipv4_size(c["cidr"])
            for r in d.get("regions", [])
            for c in r["cidrs"]
        )
        providers["oracle"] = {"ip_count": ip_count, "updated": _file_mtime("oracle_ranges.json")}
    except Exception:
        pass

    # Azure — changeNumber is a version integer, not a date; use file mtime
    try:
        with open(_json_path("azure_ranges.json")) as f:
            d = json.load(f)
        ip_count = sum(
            _ipv4_size(cidr)
            for v in d.get("values", [])
            for cidr in v["properties"]["addressPrefixes"]
        )
        providers["azure"] = {"ip_count": ip_count, "updated": _file_mtime("azure_ranges.json")}
    except Exception:
        pass

    # Cloudflare (IPv4 only — file also contains IPv6 ranges)
    try:
        with open(_json_path("cloudflare_ranges.json")) as f:
            cidrs = [line.strip() for line in f if line.strip()]
        ip_count = sum(_ipv4_size(c) for c in cidrs)
        providers["cloudflare"] = {"ip_count": ip_count, "updated": _file_mtime("cloudflare_ranges.json")}
    except Exception:
        pass

    # DigitalOcean
    try:
        with open(_json_path("digitalocean_ranges.csv")) as f:
            ip_count = sum(_ipv4_size(row[0]) for row in csv.reader(f) if row)
        providers["digitalocean"] = {"ip_count": ip_count, "updated": _file_mtime("digitalocean_ranges.csv")}
    except Exception:
        pass

    return respond(200, {"providers": providers, "last_updated": now})


# ── Lambda handler ────────────────────────────────────────

def _extract_ip(event):
    """
    Supports REST API v1 (pathParameters.proxy) and HTTP API v2 (rawPath).
    CloudFront forwards /api/<ip>, so strip the 'api/' prefix if present.
    """
    # HTTP API v2
    if event.get("version") == "2.0":
        raw = event.get("rawPath", "").strip("/")
        # raw = "api/stats" or "api/52.52.52.52"
        parts = raw.split("/", 1)
        return parts[-1] if parts else ""

    # REST API v1
    path_params = event.get("pathParameters") or {}
    proxy = path_params.get("proxy", "")
    if proxy.startswith("api/"):
        proxy = proxy[4:]
    return proxy


def lambda_handler(event, context):
    # CORS preflight
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS" or \
       event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 204, "headers": CORS, "body": ""}

    segment = _extract_ip(event)

    if segment == "stats":
        return get_stats()

    if not segment:
        return respond(200, {"usage": "GET /api/<ip>", "example": "GET /api/52.52.52.52"})

    if not (netaddr.valid_ipv4(segment) or netaddr.valid_ipv6(segment)):
        return respond(400, {"error": "Invalid IP address", "received": segment})

    ip = segment

    if aws_ranges(ip)["statusCode"] == 200:
        return aws_ranges(ip)
    if gcp_ranges(ip)["statusCode"] == 200:
        return gcp_ranges(ip)
    if azure_ranges(ip)["statusCode"] == 200:
        return azure_ranges(ip)
    if cloudflare_ranges(ip)["statusCode"] == 200:
        return cloudflare_ranges(ip)
    if digitalocean_ranges(ip)["statusCode"] == 200:
        return digitalocean_ranges(ip)
    return oracle_ranges(ip)
