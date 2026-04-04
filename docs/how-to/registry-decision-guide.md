# Registry Decision Guide for p9i SaaS

**Date**: 2026-04-03
**Status**: Decision Reference for Production Planning

---

## Executive Summary

For multi-tenant SaaS p9i deployment on K3s, choosing the right container registry is critical for:
- Security (where API keys live in image history)
- Scalability (multi-node clusters)
- Reliability (no single points of failure)
- Cost (predictable infrastructure costs)

---

## Options Comparison

### 1. Local Registry (Podman/Docker on K3s Node)

```bash
# Setup
podman run -d --name registry -p 5000:5000 registry:2

# Usage
podman tag p9i:latest localhost:5000/p9i:k8s
podman push localhost:5000/p9i:k8s
```

| Criteria | Score | Notes |
|----------|-------|-------|
| Security | ⭐⭐⭐ | API keys in image - security concern |
| Scalability | ⭐ | Single node only |
| Reliability | ⭐⭐ | Single point of failure |
| Cost | ⭐⭐⭐⭐⭐ | Free (self-hosted) |
| Complexity | ⭐⭐ | Easy setup |

**Verdict**: ✅ Good for **single-node development**, ❌ Not for production

---

### 2. GitHub Container Registry (GHCR)

```bash
# Login
echo $GITHUB_TOKEN | podman login ghcr.io -u USERNAME --password-stdin

# Push
podman tag p9i:latest ghcr.io/owner/p9i:latest
podman push ghcr.io/owner/p9i:latest
```

| Criteria | Score | Notes |
|----------|-------|-------|
| Security | ⭐⭐⭐⭐ | Immutable tags, fine-grained tokens |
| Scalability | ⭐⭐⭐⭐ | Global CDN, multi-region |
| Reliability | ⭐⭐⭐⭐⭐ | GitHub infrastructure |
| Cost | ⭐⭐⭐⭐⭐ | Free for public + 500MB private |
| Complexity | ⭐⭐ | GitHub account needed |

**Verdict**: ✅ **Recommended for most cases** - free, scalable, secure

---

### 3. Self-Hosted Registry with S3 Backend

```yaml
# docker-compose style
registry:
  image: registry:2
  ports:
    - "5000:5000"
  environment:
    REGISTRY_STORAGE: s3
    REGISTRY_STORAGE_S3_BUCKET: my-registry
    REGISTRY_STORAGE_S3_REGION: eu-central-1
    REGISTRY_STORAGE_S3_V4SIGNING: true
```

| Criteria | Score | Notes |
|----------|-------|-------|
| Security | ⭐⭐⭐⭐⭐ | Full control, behind firewall |
| Scalability | ⭐⭐⭐⭐ | S3 handles scaling |
| Reliability | ⭐⭐⭐⭐ | S3 = 99.99% uptime |
| Cost | ⭐⭐ | ~$5-10/month for S3 |
| Complexity | ⭐⭐⭐ | Requires S3 + registry setup |

**Verdict**: ✅ Good for **compliance-heavy industries** (GDPR, HIPAA)

---

### 4. AWS ECR

```bash
# Login
aws ecr get-login-password | podman login --username=AWS --password-stdin $ECR_REGISTRY

# Push
podman tag p9i:latest $ECR_REGISTRY/p9i:latest
podman push $ECR_REGISTRY/p9i:latest
```

| Criteria | Score | Notes |
|----------|-------|-------|
| Security | ⭐⭐⭐⭐⭐ | IAM integration, VPC endpoints |
| Scalability | ⭐⭐⭐⭐⭐ | AWS managed, global |
| Reliability | ⭐⭐⭐⭐⭐ | AWS SLA |
| Cost | ⭐⭐ | ~$0.10/GB/month |
| Complexity | ⭐⭐ | Already on AWS? |

**Verdict**: ✅ **Best for AWS users** - seamless integration

---

### 5. Google GCR / Artifact Registry

```bash
# Login
gcloud auth configure-docker

# Push
gcloud artifacts docker images push $REGION-docker.pkg.dev/$PROJECT/p9i/p9i:latest
```

| Criteria | Score | Notes |
|----------|-------|-------|
| Security | ⭐⭐⭐⭐⭐ | IAM, Binary Authorization |
| Scalability | ⭐⭐⭐⭐⭐ | Google infrastructure |
| Reliability | ⭐⭐⭐⭐⭐ | Google SLA |
| Cost | ⭐⭐ | ~$0.10/GB/month |
| Complexity | ⭐⭐ | Already on GCP? |

**Verdict**: ✅ **Best for GCP users**

---

### 6. Azure ACR

```bash
# Login
az acr login --name myregistry

# Push
podman tag p9i:latest myregistry.azurecr.io/p9i:latest
podman push myregistry.azurecr.io/p9i:latest
```

| Criteria | Score | Notes |
|----------|-------|-------|
| Security | ⭐⭐⭐⭐⭐ | Azure AD, private endpoints |
| Scalability | ⭐⭐⭐⭐⭐ | Azure infrastructure |
| Reliability | ⭐⭐⭐⭐⭐ | Azure SLA |
| Cost | ⭐⭐ | ~$0.10/GB/month |
| Complexity | ⭐⭐ | Already on Azure? |

**Verdict**: ✅ **Best for Azure users**

---

## Decision Matrix

| Criteria | Local | GHCR | Self-Hosted+S3 | AWS ECR | GCR | Azure ACR |
|----------|-------|------|-----------------|---------|-----|-----------|
| **Security** | 3 | 4 | 5 | 5 | 5 | 5 |
| **Scalability** | 1 | 4 | 4 | 5 | 5 | 5 |
| **Reliability** | 2 | 5 | 4 | 5 | 5 | 5 |
| **Cost** | 5 | 5 | 3 | 2 | 2 | 2 |
| **Complexity** | 5 | 4 | 3 | 4 | 4 | 4 |
| **Total** | **16** | **22** | **19** | **21** | **21** | **21** |

---

## Recommendations by Use Case

### Development / Single Node
```
Option: Local Registry (Podman)
Why: Free, simple, works for single-node
Command: make local-registry
```

### Small Team / Personal Projects
```
Option: GHCR (GitHub Container Registry)
Why: Free, no infrastructure to manage
Setup: ~10 minutes
```

### Production SaaS (Multi-node)
```
Option: AWS ECR OR GHCR + Image Signing
Why: Scalability + Security + Reliability
Additional: Enable Binary Authorization (GCP) or Sigstore (any)
```

### Enterprise / Compliance
```
Option: Self-Hosted Registry + S3 Backend
Why: Full control, GDPR compliant, no vendor lock-in
Setup: ~1 hour + S3 bucket
```

---

## Security Hardening (Required for Production)

### 1. Image Scanning
```bash
# Use Trivy for vulnerability scanning
trivy image --severity HIGH,CRITICAL myregistry/p9i:latest
```

### 2. Image Signing (Sigstore)
```bash
# Sign images with Cosign
cosign sign --key cosign.key myregistry/p9i:latest

# Verify before deployment
cosign verify --key cosign.pub myregistry/p9i:latest
```

### 3. Never Bake Secrets into Images
```dockerfile
# BAD - secrets in image layers
FROM python:3.11
ENV API_KEY=secret123  # ❌ In image history!

# GOOD - secrets at runtime
ENV API_KEY_FILE=/run/secrets/api_key  # ✅ Mount at runtime
```

---

## Migration Path

```
Phase 1: Local Registry (Day 1)
├── Setup podman registry on K3s node
├── Test deployment
└── Document procedures

Phase 2: GHCR Migration (Week 1)
├── Create GitHub account / org
├── Setup GHCR with fine-grained tokens
├── Push images to GHCR
└── Update Helm values

Phase 3: Production Hardening (Month 1)
├── Enable image signing (Cosign)
├── Add image scanning to CI/CD
├── Implement pull-not-secret policy
└── Setup multi-region replication (if needed)
```

---

## Quick Setup Commands

### Setup Local Registry (Podman)
```bash
# On K3s node
podman run -d --name registry \
  --restart=always \
  -p 5000:5000 \
  -v registry-data:/var/lib/registry \
  registry:2

# Tag and push
podman tag p9i:latest localhost:5000/p9i:k8s
podman push localhost:5000/p9i:k8s

# Update Helm
helm upgrade p9i ./helm/p9i -n p9i \
  --set image.repository=localhost:5000/p9i \
  --set image.tag=k8s \
  --set image.pullPolicy=Never
```

### Setup GHCR
```bash
# Generate fine-grained token: https://github.com/settings/tokens
# Required: write:packages

export GHCR_TOKEN="ghp_xxx"
echo $GHCR_TOKEN | podman login ghcr.io -u USERNAME --password-stdin

podman tag p9i:latest ghcr.io/USERNAME/p9i:latest
podman push ghcr.io/USERNAME/p9i:latest

# Update Helm
helm upgrade p9i ./helm/p9i -n p9i \
  --set image.repository=ghcr.io/USERNAME/p9i \
  --set image.tag=latest \
  --set image.pullPolicy=Always
```

---

## Files

- This guide: `docs/how-to/registry-decision-guide.md`
- Related: `helm/p9i/values.yaml`
- Related: `docker-compose.yml`

---

## Decision Checklist

Before going to production, verify:

- [ ] Registry selected and documented
- [ ] Image scanning configured
- [ ] Secrets handling documented (no env vars in Dockerfile)
- [ ] Rollback procedure tested
- [ ] Backup/restore for self-hosted registries
- [ ] Multi-region setup for high availability (if needed)
