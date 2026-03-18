# AI Agent Prompt: CI/CD Pipeline Management для 

**Version:** 1.2
**Date:** 2026-03-06
**Purpose:** Диагностика, оптимизация и расширение CI/CD pipeline с учётом ADR-решений

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Operational |
| **Время выполнения** | 45–90 мин |
| **Домен** | CI/CD — управление pipeline |

**Пример запроса:**

> «Используя `promt-ci-cd-pipeline.md`, проанализируй и оптимизируй CI/CD workflow:
> `<конкретный workflow или проблема>` с измеримым эффектом и списком рисков.»

**Ожидаемый результат:**
- Диагностика текущего состояния pipeline (время, ошибки, bottlenecks)
- Plan оптимизации с измеримыми метриками (время сборки, success rate)
- Обновлённые workflow файлы в `.github/workflows/`
- ADR обновлён если изменён подход к CI/CD

---

## Когда использовать

- При медленных или нестабильных CI/CD pipelines
- При добавлении нового workflow (deploy, test, lint)
- После добавления нового компонента в стек (нужна проверка pipeline coverage)
- При задачах ADR-023 DRY-консолидации CI/CD инфраструктуры

---

## Mission Statement

Ты — AI-агент, специализирующийся на **управлении CI/CD pipeline** проекта .
Твоя задача — диагностировать проблемы CI, оптимизировать время выполнения,
добавлять новые проверки и поддерживать соответствие ADR.

**Примеры задач, которые решает этот промпт:**
- Диагностика failing workflows (GitHub Actions)
- Оптимизация времени CI (параллелизация, кэширование)
- Добавление новых проверок (security scan, ADR compliance)
- Настройка CD (ArgoCD, GitOps)
- Интеграция тестов в pipeline

**Ожидаемый результат:**
- CI/CD pipeline стабильно работает
- Время выполнения оптимизировано
- Все ADR-решения проверяются в CI
- Документирован процесс deployment

---

## Контракт синхронизации системы

Этот промпт управляется из единой точки: `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md`.

Обязательные инварианты:
- Использовать topic slug для идентификации ADR
- GitOps через ArgoCD (`gitops/codeshift-application.yaml`)
- CI скрипты в `scripts/ci/` и `.github/workflows/`
- Соблюдать ADR `gitops-validation-production-deployment-monitoring`

---

## Назначение

Этот промпт стандартизирует изменения CI/CD pipeline с учётом архитектурных ограничений  и GitOps-практик.

## Входы

- Запрос на изменение/оптимизацию CI/CD
- Текущие workflow/скрипты/Make-targets и логи пайплайна
- Требования к качественным gate и политике релизов

## Выходы

- Обновлённые CI/CD конфигурации и скрипты
- Зафиксированные quality gates и критерии прохождения
- Документированный результат с верификацией

## Ограничения / инварианты

- Следовать ограничениям I-1..I-9 и Constraints C1–C10 из meta-prompt
- Сохранять topic slug-first при ссылках на ADR
- Учитывать dual-status и проверять прогресс по `verify-adr-checklist.sh` для ADR-связанных изменений
- Использовать `verify-all-adr.sh` при затрагивании архитектурных правил
- Context7 gate обязателен для выбора CI/CD практик и security controls
- Соблюдать Anti-Legacy и update in-place

## Workflow шаги

1. Discovery: собрать baseline текущего pipeline и проблемные точки
2. Design: выбрать целевую стратегию проверок и оптимизаций
3. Implementation: внести минимальные совместимые изменения
4. Validation: подтвердить стабильность и прохождение quality gates

## Проверки / acceptance criteria

- Pipeline выполняет обязательные проверки без ложных пропусков
- ADR-связанные изменения подтверждены скриптами `verify-all-adr.sh` / `verify-adr-checklist.sh`
- Нет активных ссылок на legacy-контур как на source of truth

## Связи с другими промптами

- До: `promt-verification.md` (оценка архитектурного контекста)
- После: `promt-index-update.md` (если обновлялись ADR/индекс), `promt-security-audit.md` (если добавлены security-гейты)

---

## Project Context

### CI/CD Architecture

```
GitHub Actions (CI)
├── .github/workflows/
│   ├── ci.yml          # Main CI pipeline
│   ├── docs.yml        # Documentation build
│   └── release.yml     # Release automation
│
├── scripts/ci/         # CI-specific scripts
│   └── *.sh
│
└── scripts/            # Shared scripts
    ├── test.sh
    ├── ci-install-chart-on-k3s.sh
    └── verify-all-adr.sh

ArgoCD (CD)
├── gitops/
│   ├── codeshift-application.yaml
│   ├── monitoring-application.yaml
│   └── overlays/
│       ├── dev/
│       ├── staging/
│       └── prod/
```

### Текущие CI Jobs

| Job | Trigger | Что делает |
|---|---|---|
| `lint` | PR, push | shellcheck, yamllint, helm lint |
| `test` | PR, push | pytest, unit tests |
| `build` | PR, push | Docker build (optional) |
| `deploy-preview` | PR | Ephemeral environment |
| `deploy-staging` | merge to main | ArgoCD sync staging |
| `deploy-prod` | tag/release | ArgoCD sync prod |

### ADR-related CI Checks

| ADR Topic | CI Check |
|---|---|
| `bash-formatting-standard` | shellcheck, shfmt |
| `documentation-generation` | mkdocs build |
| `e2e-testing-new-features` | E2E test suite |
| `gitops-validation` | ArgoCD dry-run |

---

## Шаг 0: Определение задачи

### 0.1. Тип задачи

| Тип | Описание | Промпт секция |
|---|---|---|
| **Diagnose** | CI/CD failing, нужен fix | Шаг 1-2 |
| **Optimize** | Ускорить pipeline | Шаг 3 |
| **Extend** | Добавить новые проверки | Шаг 4 |
| **Configure** | Настроить CD/GitOps | Шаг 5 |

---

## Шаг 1: Диагностика failing CI (если применимо)

### 1.1. Получить информацию об ошибке

```bash
# Проверить последние runs (через gh CLI)
gh run list --limit 5
gh run view [run-id] --log-failed

# Или в GitHub UI:
# Actions → выбрать workflow → выбрать run → посмотреть логи
```

### 1.2. Классифицировать ошибку

| Категория | Признаки | Решение |
|---|---|---|
| **Flaky test** | Проходит при re-run | retry механизм / fix test |
| **Environment** | Works locally, fails in CI | CI-specific deps/config |
| **Dependency** | Package install failed | Cache invalidation / version pin |
| **Resource** | OOMKilled, timeout | Increase limits / optimize |
| **Code issue** | Lint/test fails consistently | Fix code |

### 1.3. Локальное воспроизведение

```bash
# Запустить те же команды локально
make lint
make test
./scripts/verify-all-adr.sh

# Для Helm
helm lint .
helm template . -f config/values-dev.yaml --debug
```

---

## Шаг 2: Context7 — CI/CD Best Practices

### 2.1. Запросы к Context7

```
Запрос к Context7:
- Технология: GitHub Actions / ArgoCD
- Задача: [диагностика / оптимизация / новая проверка]
- Что получить: best practices, common issues, examples
```

**Примеры запросов:**

| Задача | Context7 Query |
|---|---|
| Flaky tests | `github actions retry step flaky test continue-on-error` |
| Caching | `github actions cache npm poetry pip docker layer` |
| ArgoCD sync | `argocd application sync hook wave prune` |
| Parallel jobs | `github actions matrix strategy parallel jobs` |
| Security scan | `github actions trivy snyk security scan container` |

---

## Шаг 3: Оптимизация CI Pipeline

### 3.1. Анализ текущего времени

```bash
# Посмотреть время выполнения jobs
gh run view [run-id] --json jobs | jq '.jobs[] | {name, conclusion, duration: (.completedAt | fromdateiso8601) - (.startedAt | fromdateiso8601)}'
```

### 3.2. Оптимизации

**Кэширование:**
```yaml
# .github/workflows/ci.yml
- name: Cache Poetry dependencies
  uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pypoetry
      telegram-bot/.venv
    key: ${{ runner.os }}-poetry-${{ hashFiles('telegram-bot/poetry.lock') }}
    restore-keys: |
      ${{ runner.os }}-poetry-

- name: Cache Helm dependencies
  uses: actions/cache@v4
  with:
    path: ~/.cache/helm
    key: ${{ runner.os }}-helm-${{ hashFiles('Chart.lock') }}
```

**Параллелизация:**
```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run linters
        run: make lint

  test-unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Unit tests
        run: make test-unit

  test-integration:
    needs: [lint]  # depend only on lint, not on test-unit
    runs-on: ubuntu-latest
    steps:
      - name: Integration tests
        run: make test-integration

  # test-unit и test-integration выполняются параллельно
```

**Matrix builds:**
```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
        k8s-provider: ['k3s', 'microk8s']
    runs-on: ubuntu-latest
    steps:
      - name: Test with ${{ matrix.python-version }} on ${{ matrix.k8s-provider }}
        run: ...
```

### 3.3. Метрики оптимизации

| Метрика | До | После | Target |
|---|---|---|---|
| Total CI time | X min | Y min | < 10 min |
| Lint job | X min | Y min | < 1 min |
| Test job | X min | Y min | < 5 min |
| Deploy preview | X min | Y min | < 3 min |

---

## Шаг 4: Добавление новых проверок

### 4.1. ADR Compliance Check

```yaml
# .github/workflows/ci.yml
- name: ADR Verification
  run: |
    ./scripts/verify-all-adr.sh
    if [ $? -ne 0 ]; then
      echo "❌ ADR verification failed"
      exit 1
    fi

- name: ADR Checklist Progress
  run: |
    ./scripts/verify-adr-checklist.sh --json > adr-progress.json
    # Upload as artifact for tracking
```

### 4.2. Security Scan

```yaml
- name: Security Scan - Trivy
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    scan-ref: '.'
    severity: 'CRITICAL,HIGH'
    exit-code: '1'

- name: Secret Scan - Gitleaks
  uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 4.3. Helm Chart Validation

```yaml
- name: Helm Lint
  run: helm lint .

- name: Helm Template Validation
  run: |
    helm template . -f config/values-dev.yaml > /tmp/manifests.yaml
    kubectl apply --dry-run=client -f /tmp/manifests.yaml

- name: Helm Docs Check
  run: |
    helm-docs
    git diff --exit-code README.md
```

### 4.4. Documentation Build

```yaml
- name: Build Docs
  run: |
    poetry install --with docs
    poetry run mkdocs build --strict
```

---

## Шаг 5: ArgoCD / GitOps Configuration

### 5.1. Application YAML

```yaml
# gitops/codeshift-application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: codeshift
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/codeshift.git
    targetRevision: HEAD
    path: .
    helm:
      valueFiles:
        - config/values-prod.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: codeshift
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

### 5.2. Sync Waves (порядок deployment)

```yaml
# In Helm templates, add annotations:
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "0"  # First: secrets, configmaps
    # sync-wave: "1" — Second: PVCs, storage
    # sync-wave: "2" — Third: deployments
    # sync-wave: "3" — Fourth: services, ingress
```

### 5.3. Health Checks

```yaml
# Custom health check for specific resources
spec:
  source:
    plugin:
      name: argocd-vault-plugin  # if using secrets plugin
  ignoreDifferences:
    - group: ""
      kind: Secret
      jsonPointers:
        - /data
```

---

## Шаг 6: Документирование Pipeline

### 6.1. Pipeline Overview в README

```markdown
## CI/CD Pipeline

### Continuous Integration

| Stage | Trigger | Checks |
|---|---|---|
| Lint | Every PR | shellcheck, yamllint, helm lint |
| Test | Every PR | pytest, ADR verification |
| Security | Every PR | Trivy, Gitleaks |
| Docs | Every PR | mkdocs build |

### Continuous Deployment

| Environment | Trigger | ArgoCD App |
|---|---|---|
| Preview | PR opened | auto-generated |
| Staging | Merge to main | codeshift-staging |
| Production | Release tag | codeshift-prod |
```

### 6.2. Troubleshooting Guide

```markdown
## CI Troubleshooting

### Common Issues

**Q: Lint fails but works locally**
A: Check shell/env differences. Run `make lint` in CI-like environment.

**Q: Tests timeout**
A: Check for network dependencies. Increase timeout or mock external calls.

**Q: ArgoCD sync stuck**
A: Check `argocd app get codeshift` for details. Common: resource quota, PVC issues.
```

---

## Чеклист CI/CD Changes

- [ ] Задача определена (diagnose/optimize/extend/configure)
- [ ] Context7 запрос выполнен
- [ ] Локальное воспроизведение (для diagnose)
- [ ] Изменения в `.github/workflows/` или `scripts/ci/`
- [ ] Тесты pipeline (push to branch, check run)
- [ ] Время выполнения измерено (для optimize)
- [ ] ADR compliance сохранён
- [ ] Документация обновлена
- [ ] Commit message соответствует стандарту

---

## CI/CD Files Reference

| File | Purpose |
|---|---|
| `.github/workflows/ci.yml` | Main CI pipeline |
| `.github/workflows/docs.yml` | Documentation build |
| `scripts/ci/` | CI-specific scripts |
| `scripts/test.sh` | Test runner |
| `scripts/verify-all-adr.sh` | ADR verification |
| `gitops/codeshift-application.yaml` | ArgoCD app definition |
| `gitops/overlays/` | Environment-specific configs |

---

## Ресурсы

| Ресурс | Путь | Назначение |
|---|---|---|
| **ADR-файлы** | `docs/explanation/adr/ADR-*.md` | Architecture constraints |
| **Скрипт верификации** | `scripts/verify-all-adr.sh` | Validation |
| **CI configuration** | `.github/workflows/`, `scripts/ci/` | Pipelines |
| **Правила проекта** | `.github/copilot-instructions.md` | Test modes, lint rules |
| **K8s abstraction** | `scripts/helpers/k8s-exec.sh` | kubectl wrapper |
| **Официальная документация** | `docs/official_document/` | **READ-ONLY** эталон |
| **Meta-prompt** | `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md` | Source of truth |

---

## Связанные промпты

| Промпт | Когда использовать |
|---|---|
| `promt-verification.md` | Проверка ADR после CI changes |
| `promt-feature-add.md` | Если CI change требует нового ADR |
| `promt-security-audit.md` | Добавление security checks |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.2 | 2026-03-06 | Добавлены секции Gate I: `## Быстрый старт`, `## Когда использовать`, `## Журнал изменений`. |
| 1.1 | 2026-02-25 | Добавлены `## Чеклист`, `## Связанные промпты`; unified Mission Statement. |
| 1.0 | 2026-02-24 | Первая версия: CI/CD pipeline management с ADR-решениями. |

---

**Prompt Version:** 1.2
**Date:** 2026-03-06
