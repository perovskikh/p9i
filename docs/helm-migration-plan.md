# Helm Migration Plan: K8s Consolidation

## Цель
Удалить дублирующиеся K8s манифесты, оставить **только Helm** как единый источник истины для deployment.

## Scope (Что НЕ удалять)
- `k8s/00-namespace.yaml` — namespace
- `k8s/02-db-redis.yaml` — DB + Redis (shared infrastructure)

## Scope (Что удалить)
- `k8s/03-mcp-server.yaml` — дублирует Helm deployment
- `k8s/04-ingress.yaml` — дублирует Helm ingress
- `k8s/04-hpa.yaml` — нужно добавить в Helm
- `k8s/01-nginx-config.yaml` — интегрировать в Helm или удалить

---

## Этапы

### Phase 1: Review & Sync (ТЕКУЩИЙ)
- [x] Проанализировать k8s/*.yaml
- [x] Проанализировать helm/p9i/templates/*.yaml
- [x] Выявить различия

### Phase 2: Helm Updates
- [ ] Добавить HPA в Helm templates
- [ ] Синхронизировать values из k8s манифеста
- [ ] Обновить ingress path: `/` → `/mcp`

### Phase 3: Cleanup
- [ ] Удалить дублирующиеся манифесты
- [ ] Обновить Makefile

### Phase 4: Verification
- [ ] Запустить helm lint
- [ ] Проверить diff

---

## Сравнение K8s vs Helm

| Компонент | K8s (текущий) | Helm (целевой) | Статус |
|-----------|---------------|----------------|--------|
| Deployment | k8s/03-mcp-server.yaml | helm templates/deployment.yaml | ✅ Готов |
| Service | Встроен в 03-mcp-server.yaml | helm templates/service.yaml | ✅ Готов |
| Ingress | k8s/04-ingress.yaml | helm templates/ingress.yaml | ⚠️ path=/ нужно /mcp |
| HPA | k8s/04-hpa.yaml | ОТСУТСТВУЕТ | ❌ Добавить |
| Namespace | k8s/00-namespace.yaml | helm hook | ⬇️ Оставить |
| DB/Redis | k8s/02-db-redis.yaml | helm (bitnami charts) | ⬇️ Оставить |

---

## Ключевые изменения

### 1. Ingress path
```yaml
# Текущий (k8s)
path: /mcp

# Текущий (Helm)
path: /  # НЕПРАВИЛЬНО
```

### 2. HPA (нужно добавить)
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
...
```

### 3. Resources (K8s более актуальные)
```yaml
# K8s (03-mcp-server.yaml)
requests:
  memory: "256Mi"
  cpu: "250m"
limits:
  memory: "512Mi"
  cpu: "1000m"

# Helm (values.yaml)
requests:
  memory: "512Mi"  # НЕПРАВИЛЬНО
  cpu: "250m"
limits:
  memory: "1Gi"    # НЕПРАВИЛЬНО
  cpu: "1000m"
```
