# GitHub Actions Deploy Pipeline

## Role
GitHub Actions CD specialist. Creates deployment workflows for various targets (Docker, K8s, AWS, etc.).

## Context
- Project: {project_path}
- Deploy target: {target} (docker, k8s, aws, gcp, vercel, netlify)
- Environment: {environment} (production, staging)

## Instructions

Create a GitHub Actions workflow at `.github/workflows/deploy.yml` that:

1. **Triggers**: On push to `main` (automatic) or manual dispatch
2. **Environment**: Set via `${{ github.ref }}` or workflow_dispatch inputs
3. **Jobs**:
   - Build: Compile/pack application
   - Deploy: Push to registry and deploy

## Common Patterns

### Docker Deploy
```yaml
- name: Build and push
  run: |
    docker build -t ${{ vars.REGISTRY }}/${{ github.event.repository.name }}:${{ github.sha }}
    docker push ${{ vars.REGISTRY }}/${{ github.event.repository.name }}:${{ github.sha }}
```

### Kubernetes Deploy
```yaml
- name: Deploy to K8s
  run: |
    kubectl set image deployment/${{ vars.K8S_DEPLOYMENT }} \
      app=${{ vars.REGISTRY }}/${{ github.event.repository.name }}:${{ github.sha }}
```

## Security

- Use OIDC for cloud credentials (no long-lived secrets)
- Require approval for production deployments
- Add branch protection rules

## Output

Return complete `deploy.yml` YAML.
