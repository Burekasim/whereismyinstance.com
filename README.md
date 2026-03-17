# WhereIsMyInstance.com

Instantly identify which cloud provider owns any IP address — and exactly which region, service, or network it belongs to.

Supports **AWS, Azure, GCP, Cloudflare, Oracle Cloud, and DigitalOcean**.

## Architecture

```
User → CloudFront → /api/*  → API Gateway (HTTP v2) → Lambda
                  → default → S3 (static frontend)
```

- **Frontend** — single-page `index.html` served from S3 via CloudFront
- **API** — Python 3.12 Lambda behind API Gateway, callable at `/api/<ip>`
- **IP data** — provider range files bundled inside the Lambda zip, refreshed daily by a GitHub Actions cron job

## API

```
GET /api/<ip>
GET /api/stats
```

### Lookup example

```bash
curl https://whereismyinstance.com/api/52.52.52.52
```

```json
{
  "cloud": "Amazon Web Services",
  "ip_range": "52.52.0.0/15",
  "region": "us-west-2",
  "region_location": "US West (Oregon)",
  "service": ["AMAZON", "EC2"]
}
```

### Stats example

```bash
curl https://whereismyinstance.com/api/stats
```

```json
{
  "providers": {
    "aws":          { "count": 7318,  "updated": "2026-03-17T..." },
    "gcp":          { "count": 654,   "updated": "2026-03-17T..." },
    "azure":        { "count": 59833, "updated": "2026-03-17T..." },
    "oracle":       { "count": 1482,  "updated": "2026-03-17T..." },
    "cloudflare":   { "count": 15,    "updated": "2026-03-17T..." },
    "digitalocean": { "count": 1502,  "updated": "2026-03-17T..." }
  },
  "last_updated": "2026-03-17T02:05:00Z"
}
```

## Project structure

```
.
├── index.html                          # Frontend SPA
├── lambda/
│   ├── lambda_function.py              # Lambda handler
│   ├── requirements.txt                # netaddr
│   └── json/                           # IP range files (gitignored, downloaded by CI)
├── scripts/
│   └── download_ip_ranges.py           # Downloads latest files from all 6 providers
├── terraform/
│   ├── providers.tf                    # AWS + S3 backend
│   ├── variables.tf
│   ├── main.tf                         # Lambda, API GW, S3, CloudFront, Route 53
│   └── outputs.tf
└── .github/workflows/
    ├── deploy.yml                      # Triggered on push to main
    └── update-ip-ranges.yml            # Daily cron — refreshes IP data + redeploys Lambda
```

## CI/CD

### `deploy.yml` — triggered on push to `main`

1. Download IP range files
2. Install Lambda dependencies & build zip
3. `terraform apply` (infrastructure changes)
4. `aws lambda update-function-code`
5. `aws s3 sync` frontend
6. CloudFront invalidation

### `update-ip-ranges.yml` — daily at 02:00 UTC

1. Download latest IP range files from all providers
2. Rebuild Lambda zip with fresh data
3. `aws lambda update-function-code`
4. Smoke-test invoke against `52.52.52.52`

## Deployment

### Prerequisites

- AWS account with a Route 53 hosted zone and an ACM certificate (in `us-east-1`) for your domain
- An S3 bucket for Terraform state
- GitHub Actions secrets/vars configured (see below)

### First deploy

```bash
# 1. Download IP range files locally
python scripts/download_ip_ranges.py

# 2. Install Lambda deps
pip install -r lambda/requirements.txt -t lambda/

# 3. Init Terraform
cd terraform
terraform init \
  -backend-config="bucket=<your-tf-state-bucket>" \
  -backend-config="key=whereismyinstance/terraform.tfstate" \
  -backend-config="region=us-east-1"

# 4. Apply
terraform apply \
  -var="domain_name=whereismyinstance.com" \
  -var="hosted_zone_id=<zone-id>" \
  -var="acm_certificate_arn=<cert-arn>"
```

After that, all subsequent deploys are handled automatically by GitHub Actions on push to `main`.

### GitHub Actions secrets & variables

| Name | Type | Description |
|---|---|---|
| `AWS_ROLE_ARN` | secret | IAM role ARN for OIDC assumption |
| `AWS_ROLE_ARN` | secret | IAM role ARN for OIDC assumption |
| `AWS_REGION` | var | e.g. `us-east-1` |
| `TF_BACKEND_BUCKET` | var | S3 bucket name for Terraform state |
| `CLOUDFRONT_DISTRIBUTION_ID` | var | Existing CloudFront distribution ID |
| `LAMBDA_FUNCTION_NAME` | var | `whereismyinstance-api` (set after first deploy) |

## IP range sources

| Provider | Source |
|---|---|
| AWS | https://ip-ranges.amazonaws.com/ip-ranges.json |
| GCP | https://www.gstatic.com/ipranges/cloud.json |
| Azure | https://www.microsoft.com/en-us/download/details.aspx?id=56519 |
| Oracle | https://docs.oracle.com/en-us/iaas/tools/public_ip_ranges.json |
| Cloudflare | https://www.cloudflare.com/ips-v4 + /ips-v6 |
| DigitalOcean | https://digitalocean.com/geo/google.csv |

## Built by

[Avi Keinan](https://www.linkedin.com/in/avi-keinan-14828738/)
