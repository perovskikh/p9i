# p9i Helm Chart for MicroK8s Deployment

Полная документация для развёртывания p9i MCP server в MicroK8s с использованием Helm и python CLI.

## 📋 Содержание

- [Быстрый старт](#быстрый-старт)
- [Требования](#требования)
- [Python CLI](#python-cli)
- [Helm развёртывание](#helm-развёртывание)
- [Idempotentность и hooks](#idempotentность-и-hooks)
- [Конфигурация окружений](#конфигурация-окружений)
- [Backup и Restore](#backup-и-restore)
- [CI/CD](#cicd)
- [Отладка](#отладка)

## 🚀 Быстрый старт

```bash
# 1. Проверка MicroK8s
microk8s status

# 2. Включение необходимых аддонов
microk8s enable storage dns ingress

# 3. Python CLI - развёртывание
python -m cli.main deploy apply

# 4. Проверка статуса
python -m cli.main deploy status
```

## Требования

- **MicroK8s** v1.20+
- **kubectl** настроенный для MicroK8s
- **Helm** v3.8+
- **Docker** для сборки образов

### Установка MicroK8s

```bash
# Ubuntu/Debian
sudo snap install microk8s --classic

# Или через скрипт
curl -s https://get.microk8s.io | sh

# Включение аддонов
microk8s enable storage dns ingress metrics-server
microk8s start
```

## Python CLI

### Установка зависимостей

```bash
pip install -r requirements-cli.txt  # если есть
```

### Команды

```bash
# Docker
python -m cli.main build                    # Сборка образа
python -m cli.main run                       # Запуск в stdio режиме
python -m cli.main start                     # Build + run

# Kubernetes/MicroK8s
python -m cli.main deploy status             # Статус развёртывания
python -m cli.main deploy apply              # Развёртывание в K8s
python -m cli.main deploy logs --tail 100    # Просмотр логов
python -m cli.main deploy restart            # Перезапуск
python -m cli.main deploy backup             # Backup PostgreSQL/Redis
python -m cli.main deploy restore --file backup.sql  # Restore
python -m cli.main deploy cleanup            # Удаление
```

### Опции deploy apply

```bash
python -m cli.main deploy apply --atomic  # Атомарное развёртывание (откат при ошибке)
```

## Helm развёртывание

### Валидация чарта

```bash
# Линтинг
helm lint ./helm/p9i

# Тестирование рендеринга
helm template p9i-test ./helm/p9i --debug
```

### Ручное развёртывание

```bash
# Создание namespace
kubectl create namespace p9i

# Установка
helm upgrade --install p9i ./helm/p9i \
  --namespace p9i \
  --create-namespace \
  --wait \
  --timeout 10m

# Обновление
helm upgrade p9i ./helm/p9i --namespace p9i

# Откат
helm rollback p9i --namespace p9i

# Удаление
helm uninstall p9i --namespace p9i
```

## Idempotentность и Hooks

Helm чарт включает pre/post hooks для idempotentных операций:

### Pre-Install/Upgrade Hook

Проверяет состояние кластера перед установкой:
- Проверка доступности storageclass `microk8s-hostpath`
- Проверка существующих PVC
- Верификация CRD

### Post-Install/Upgrade Hook

Выполняет верификацию после установки:
- Ожидание rollout статуса
- Проверка готовности pods
- Логирование состояния сервисов

### Использование

```bash
# Idempotentная установка (безопасная для повторного запуска)
helm upgrade --install p9i ./helm/p9i \
  --namespace p9i \
  --wait \
  --atomic \
  --timeout 15m

# При успехе - продолжает, при ошибке - автоматически откатывает
```

## Конфигурация окружений

### Development (values-dev.yaml)

```bash
helm upgrade --install p9i ./helm/p9i \
  --namespace p9i-dev \
  --create-namespace \
  --values ./helm/p9i/values-dev.yaml
```

### Production (values-prod.yaml)

```bash
helm upgrade --install p9i ./helm/p9i \
  --namespace p9i \
  --create-namespace \
  --values ./helm/p9i/values-prod.yaml \
  --wait \
  --timeout 15m \
  --atomic
```

### Ключевые отличия

| Параметр | Dev | Prod |
|----------|-----|------|
| Replicas | 1 | 2 |
| Resources | 512Mi | 2Gi |
| Persistence | false | true (20Gi) |
| Ingress | false | true |
| JWT | false | true |

## Backup и Restore

### Автоматический backup через CLI

```bash
# Backup
python -m cli.main deploy backup
# Создаёт: p9i_postgres_YYYYMMDD_HHMMSS.sql и p9i_redis_YYYYMMDD_HHMMSS.rdb

# Restore
python -m cli.main deploy restore --file p9i_postgres_20260326.sql
```

### Ручной backup

```bash
# PostgreSQL
kubectl exec -n p9i p9i-p9i-postgresql-0 -- \
  pg_dump -U postgres ai_prompts > backup.sql

# Restore
kubectl exec -i -n p9i p9i-p9i-postgresql-0 -- \
  psql -U postgres ai_prompts < backup.sql

# Redis
kubectl exec -n p9i p9i-p9i-redis-master-0 -- redis-cli SAVE
kubectl cp n9i/p9i-p9i-redis-master-0:/data/dump.rdb ./redis_backup.rdb
```

## CI/CD

### GitHub Actions

Workflow файл: `.github/workflows/helm-deploy.yml`

```bash
# Триггер вручную для deployment
gh workflow run helm-deploy.yml -f environment=prod
```

### Валидация в CI

```bash
# 1. Helm lint
helm lint ./helm/p9i

# 2. Template test
helm template test ./helm/p9i --debug

# 3. Docker build test
docker build -f docker/Dockerfile -t p9i:test .

# 4. Smoke test
docker run -d --name p9i-test p9i:test
curl -f http://localhost:8000/health
docker rm -f p9i-test
```

## Отладка

### Проверка статуса

```bash
# Все ресурсы
kubectl get all -n p9i

# Pods с деталями
kubectl get pods -n p9i -o wide

# Events
kubectl get events -n p9i --sort-by='.lastTimestamp'

# Helm release
helm list -n p9i
helm status p9i -n p9i
```

### Логи

```bash
# Логи приложения
kubectl logs -n p9i deployment/p9i-p9i -f --tail=100

# Логи PostgreSQL
kubectl logs -n p9i statefulset/p9i-p9i-postgresql -f --tail=50

# Логи Redis
kubectl logs -n p9i statefulset/p9i-p9i-redis-master -f --tail=50
```

### Диагностика

```bash
# Describe resources
kubectl describe deployment/p9i-p9i -n p9i
kubectl describe pod -l app=p9i -n p9i

# Port forward для тестирования
kubectl port-forward -n p9i svc/p9i-p9i 8000:8000

# Health check
curl http://localhost:8000/health
```

### Частые проблемы

| Проблема | Решение |
|----------|---------|
| Pod в Pending | Проверить storage: `kubectl get pvc -n p9i` |
| ImagePullBackOff | Проверить registry и тег образа |
| CrashLoopBackOff | Логи: `kubectl logs --previous` |
| Connection refused | Проверить сервисы: `kubectl get svc -n p9i` |

## Структура файлов

```
p9i/
├── helm/p9i/
│   ├── Chart.yaml           # Метаданные чарта
│   ├── values.yaml          # Значения по умолчанию
│   ├── values-dev.yaml      # Dev окружение
│   ├── values-prod.yaml     # Prod окружение
│   └── templates/
│       ├── _helpers.tpl     # Шаблонные функции
│       ├── deployment.yaml  # Deployment
│       ├── service.yaml     # Service
│       ├── ingress.yaml     # Ingress (Traefik)
│       ├── secret.yaml      # Secrets
│       ├── pre-install-hook.yaml   # Pre-install checks
│       ├── post-install-hook.yaml  # Post-install verification
│       └── k8s/manifests.yaml      # Plain K8s manifests
├── cli/
│   └── main.py              # Python CLI
└── .github/workflows/
    └── helm-deploy.yml      # CI/CD workflow
```

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|-----------|--------------|
| `P9I_API_KEY` | API ключ для авторизации | - |
| `LLM_PROVIDER` | LLM провайдер (auto/zai/minimax/deepseek) | auto |
| `JWT_ENABLED` | Включить JWT авторизацию | false |
| `LOG_LEVEL` | Уровень логирования | INFO |
| `ALLOWED_ORIGINS` | CORS allowed origins | * |

## Безопасность

### Secrets

Чувствительные данные хранятся в Kubernetes Secrets:
- LLM API ключи (ZAI, Anthropic, MiniMax, DeepSeek)
- JWT secret
- Figma token

```bash
# Просмотр secrets
kubectl get secrets -n p9i

# Добавление нового secret
kubectl create secret generic p9i-secrets \
  --from-literal=zai-key=YOUR_KEY \
  -n p9i
```

### Network Policy (опционально)

Для production рекомендуется добавить NetworkPolicy:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: p9i-network-policy
  namespace: p9i
spec:
  podSelector:
    matchLabels:
      app: p9i
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: p9i
  egress:
    - to:
        - namespaceSelector: {}
```

---

**Версия**: 1.0.0
**Обновлено**: 2026-03-26