# AI Agent Prompt: Аудит безопасности (Universal)

> **NOTE:** This is a UNIVERSAL prompt that auto-adapts to any project structure.
> All project-specific references use `${VARIABLE}` placeholders.

**Version:** 1.2
**Date:** 2026-03-06
**Purpose:** Комплексный аудит безопасности ${PROJECT_TYPE} с платёжной интеграцией ${PAYMENT_PROVIDER}

---

## Быстрый старт

| Параметр | Значение |
|----------|----------|
| **Тип промпта** | Operational |
| **Время выполнения** | 90–180 мин |
| **Домен** | Security — аудит безопасности |

**Пример запроса:**

> «Используя `promt-security-audit.md`, проведи аудит безопасности по компонентам:
> `<${PRIMARY_INTERFACE} Bot / ${PAYMENT_PROVIDER} webhooks / K8s secrets>`
> и выдай приоритизированный remediation plan.»

**Ожидаемый результат:**
- Security findings по компонентам (Critical / High / Medium / Low)
- Приоритизированный remediation plan с effort estimates
- ADR обновлён если найдены архитектурные security gaps
- Список immediate actions (без ADR — просто фикс)

---

## Когда использовать

- Перед production release фичи с чувствительными данными
- При интеграции платёжных систем (${PAYMENT_PROVIDER} webhooks, HMAC)
- При подозрении на security vulnerability (из CVE, audit, code review)
- Плановый quarterly security review
- После обнаружения ADR-расхождения в области безопасности

> **Обязательно для:** HMAC validation, secrets management, K8s RBAC, payment webhooks.

---

## Mission Statement

Ты — AI-агент, специализирующийся на **аудите безопасности** проекта .
Твоя задача — выявить уязвимости, проверить соответствие best practices безопасности
и обеспечить защиту платёжных данных и пользовательской информации.

**Примеры задач, которые решает этот промпт:**
- Аудит RBAC конфигураций в Kubernetes
- Проверка Network Policies
- Валидация webhook HMAC (${PAYMENT_PROVIDER})
- Аудит secrets management
- Проверка SQL injection prevention
- Анализ rate limiting конфигураций
- Проверка JWT token handling
- Аудит TLS/SSL конфигураций

**Ожидаемый результат:**
- Отчёт о найденных уязвимостях (Critical/High/Medium/Low)
- Рекомендации по исправлению
- Проверка соответствия ADR-решениям по безопасности
- Plan remediation с приоритетами

---

## Контракт синхронизации системы

Этот промпт управляется из единой точки: `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md`.

Обязательные инварианты синхронизации:
- Использовать topic slug как первичный идентификатор ADR
- Перед аудитом выполнять Context7 gate для актуальных best practices
- Считать `docs/official_document/` строго READ-ONLY
- Никогда не выводить реальные secrets/passwords в отчёты

---

## Назначение

Этот промпт выполняет security-аудит платформы с фиксацией рисков, remediation-плана и ADR-соответствия.

## Входы

- Scope и приоритетные зоны аудита (auth, data, payment, network, containers)
- Текущие конфигурации, код и процессы деплоя
- Требования compliance и внутренние security-политики

## Выходы

- Структурированный security report (findings, severity, remediation)
- Приоритизированный план устранения уязвимостей
- Обновления ADR/индекса при архитектурных последствиях

## Ограничения / инварианты

- Следовать ограничениям I-1..I-9 и Constraints C1–C10 из meta-prompt
- Идентифицировать ADR по topic slug
- Учитывать dual-status и проверять прогресс через `verify-adr-checklist.sh` при ADR-затронутых изменениях
- Использовать `verify-all-adr.sh` для архитектурной валидации
- Context7 gate обязателен для security best practices
- Соблюдать Anti-Legacy и update in-place

## Workflow шаги

1. Discovery: определить threat surface и границы аудита
2. Audit: провести проверки по слоям безопасности
3. Prioritize: классифицировать риски и сформировать remediation roadmap
4. Validate: подтвердить реалистичность мер и связать с архитектурой

## Проверки / acceptance criteria

- Все findings имеют severity, impact и actionable remediation
- Критические риски имеют первоочередной план исправления
- ADR/индекс обновлены, если выводы меняют архитектурные решения

## Связи с другими промптами

- До: `promt-verification.md`, `promt-ci-cd-pipeline.md`
- После: `promt-bug-fix.md`, `promt-index-update.md`, `promt-adr-implementation-planner.md`

---

## Project Context

### О проекте (Security-relevant)

**${PROJECT_NAME}** — ${PROJECT_TYPE} с критичными security requirements:

| Компонент | Security Concern |
|---|---|
| **${PAYMENT_PROVIDER} payments** | PCI DSS, webhook HMAC validation, idempotency |
| **${PRIMARY_INTERFACE} Bot** | User authentication, bot token protection |
| **PostgreSQL** | SQL injection, credential management |
| **Kubernetes** | RBAC, Network Policies, Secrets |
| **JWT Auth** | Token signing, expiration, refresh |
| **Ingress (Traefik)** | TLS termination, rate limiting, middlewares |

### Security-relevant ADR Topics

| Topic Slug | Security Aspect |
|---|---|
| `${PLATFORM_SLUG}` | Webhook HMAC, JWT, pydantic-settings (no hardcode) |
| `unified-auth-architecture` | Auth flow, token management |
| `path-based-routing` | Single domain → easier SSL/TLS |
| `k8s-provider-abstraction` | No hardcoded credentials |

## Ресурсы

| Ресурс | Путь | Назначение |
|---|---|---|
| **ADR-файлы** | `docs/explanation/adr/ADR-*.md` | ADR-соответствие для security |
| **Скрипт верификации** | `scripts/verify-all-adr.sh` | Валидация архитектуры |
| **Скрипт прогресса** | `scripts/verify-adr-checklist.sh` | Прогресс реализации security-функций |
| **Правила проекта** | `.github/copilot-instructions.md` | Security-relevant ADR topics |
| **Официальная документация** | `docs/official_document/` | **READ-ONLY** эталон security best practices |
| **Meta-prompt** | `docs/ai-agent-prompts/meta-promptness/meta-promt-adr-system-generator.md` | Source of truth |

---

## Шаг 0: Определение scope аудита

### 0.1. Тип аудита

| Тип | Scope | Время |
|---|---|---|
| **Quick scan** | Критические точки (secrets, RBAC, webhooks) | 30 мин |
| **Standard** | Все компоненты, средняя глубина | 2-4 часа |
| **Deep dive** | Полный аудит + code review + pen test prep | 8+ часов |

### 0.2. Фокус аудита (выбрать)

- [ ] **Authentication & Authorization** (JWT, Telegram auth, RBAC)
- [ ] **Data Protection** (Secrets, DB credentials, PII)
- [ ] **Payment Security** (${PAYMENT_PROVIDER}, HMAC, idempotency)
- [ ] **Network Security** (TLS, Network Policies, Ingress)
- [ ] **Container Security** (Image scanning, Pod Security)
- [ ] **All of the above** (Full audit)

---

## Шаг 1: Context7 — Актуальные Security Best Practices

### 1.1. Запросы к Context7

```
Запрос к Context7:
- Технология: [компонент из scope]
- Задача: security best practices, common vulnerabilities, OWASP
- Что получить: checklist, anti-patterns, CVE awareness
```

**Примеры запросов:**

| Компонент | Context7 Query |
|---|---|
| ${PAYMENT_PROVIDER} | `payment webhook security hmac signature validation replay attack` |
| JWT | `jwt security best practices expiration refresh token rotation` |
| PostgreSQL | `postgresql security injection prepared statements credentials` |
| Kubernetes | `kubernetes rbac security pod security policy network policy` |
| Traefik | `traefik security rate limiting tls middleware headers` |

---

## Шаг 2: Authentication & Authorization Audit

### 2.1. JWT Token Security

```bash
# Проверить JWT конфигурацию
grep -rn "JWT\|jwt\|token\|secret" ${PROJECT_ROOT}/src/auth/ --include="*.py"
grep -rn "JWT_SECRET\|JWT_ALGORITHM\|JWT_EXPIRE" ${PROJECT_ROOT}/src/config.py

# Checklist:
# [ ] JWT_SECRET из env var (не hardcoded)
# [ ] Достаточная длина secret (>= 32 bytes)
# [ ] Appropriate algorithm (HS256 минимум, RS256 предпочтительно)
# [ ] Token expiration настроен
# [ ] Refresh token механизм (если long sessions)
```

**Критические проверки JWT:**

| Check | Requirement | Status |
|---|---|---|
| Secret source | `os.environ` или pydantic Settings | |
| Secret length | >= 256 bits | |
| Algorithm | HS256/RS256/ES256 | |
| Expiration | <= 24h для access token | |
| Refresh | Если >24h сессии | |

### 2.2. Telegram Authentication

```bash
# Проверить Telegram auth
grep -rn "TELEGRAM_BOT_TOKEN\|bot_token" ${PROJECT_ROOT}/src/ --include="*.py"
grep -rn "check_telegram_authorization\|validate" ${PROJECT_ROOT}/src/auth/ --include="*.py"

# Checklist:
# [ ] BOT_TOKEN из env var
# [ ] BOT_TOKEN не логируется
# [ ] Telegram hash validation (data-check-string)
# [ ] Auth timestamp validation (< 24h)
```

### 2.3. Kubernetes RBAC

```bash
# Проверить RBAC конфигурации
cat templates/rbac-preinstall.yaml
cat config/manifests/${PROJECT_NAME_LOWER}-rbac.yaml

# Checklist:
# [ ] Minimal privileges (не cluster-admin)
# [ ] ServiceAccount per component
# [ ] RoleBinding (не ClusterRoleBinding) where possible
# [ ] No wildcard permissions (*) без необходимости
```

**RBAC Audit Matrix:**

| ServiceAccount | Namespace | Permissions | Concern |
|---|---|---|---|
| `${PROJECT_NAME_LOWER}` | `${K8S_NAMESPACE}` | | |
| `code-server` | `codeshift` | | |
| `default` | (any) | Should be restricted | |

---

## Шаг 3: Data Protection Audit

### 3.1. Secrets Management

```bash
# Найти все секреты
grep -rn "password\|secret\|token\|key" config/ templates/ --include="*.yaml" | grep -v "#"
grep -rn "os\.environ\|getenv" ${PROJECT_ROOT}/src/ --include="*.py"

# Проверить .env.example (не должен содержать реальных значений)
cat .env.example

# Checklist:
# [ ] Все secrets в env vars
# [ ] .env в .gitignore
# [ ] .env.example без реальных значений
# [ ] Kubernetes Secrets (не ConfigMaps) для credentials
# [ ] Secrets не в логах (проверить logging)
```

**Secrets Inventory:**

| Secret | Source | Storage | Concern |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | env | K8s Secret | |
| `JWT_SECRET` | env | K8s Secret | |
| `YOOKASSA_SECRET_KEY` | env | K8s Secret | |
| `POSTGRES_PASSWORD` | env | K8s Secret | |
| `YOOKASSA_WEBHOOK_SECRET` | env | K8s Secret | |

### 3.2. Database Security

```bash
# Проверить SQL queries на injection
grep -rn "execute\|raw_sql\|text(" ${PROJECT_ROOT}/src/ --include="*.py"
grep -rn "f\".*SELECT\|f'.*SELECT" ${PROJECT_ROOT}/src/ --include="*.py"

# Проверить DB credentials
grep -rn "POSTGRES\|DATABASE_URL" ${PROJECT_ROOT}/src/config.py

# Checklist:
# [ ] Parameterized queries (не string concatenation)
# [ ] ORM (SQLAlchemy) для queries
# [ ] DB credentials из env vars
# [ ] Minimal DB user privileges
# [ ] Connection encryption (SSL/TLS)
```

### 3.3. PII Protection

```bash
# Найти обработку PII
grep -rn "email\|phone\|name\|user_id\|telegram_id" ${PROJECT_ROOT}/src/ --include="*.py" | head -20

# Checklist:
# [ ] PII не логируется в plain text
# [ ] PII зашифрована at rest (если требуется)
# [ ] Data retention policy
# [ ] GDPR compliance (если EU users)
```

---

## Шаг 4: Payment Security Audit (${PAYMENT_PROVIDER})

### 4.1. Webhook HMAC Validation

```bash
# Найти webhook handler
grep -rn "webhook\|${PAYMENT_PROVIDER_lower}" ${PROJECT_ROOT}/src/payments/ --include="*.py"

# Проверить HMAC validation
grep -rn "hmac\|signature\|verify" ${PROJECT_ROOT}/src/payments/ --include="*.py"
```

**${PAYMENT_PROVIDER} Security Checklist:**

| Check | Requirement | File | Status |
|---|---|---|---|
| HMAC validation | Before processing any webhook | `app/payments/webhooks.py` | |
| Idempotency keys | For payment creation | `app/payments/service.py` | |
| Webhook secret | From env var, not hardcoded | `app/config.py` | |
| IP whitelist | ${PAYMENT_PROVIDER} IPs only (optional) | Ingress/firewall | |
| Replay protection | Check timestamp/idempotency | `app/payments/webhooks.py` | |
| HTTPS only | Webhook endpoint | Ingress TLS | |

### 4.2. Payment Data Handling

```bash
# Проверить что payment data не логируется
grep -rn "log\|print\|logger" ${PROJECT_ROOT}/src/payments/ --include="*.py" | grep -i "card\|payment\|secret"

# Checklist:
# [ ] Card data не обрабатывается (redirect to ${PAYMENT_PROVIDER})
# [ ] Payment amounts validated server-side
# [ ] Currency validated
# [ ] Webhook events logged для audit trail
```

---

## Шаг 5: Network Security Audit

### 5.1. TLS/SSL Configuration

```bash
# Проверить cert-manager конфигурацию
cat templates/certificate.yaml
cat templates/clusterissuer.yaml

# Проверить ingress TLS
grep -A10 "tls:" templates/ingress*.yaml

# Checklist:
# [ ] TLS 1.2+ (не TLS 1.0/1.1)
# [ ] Valid certificate (not self-signed in prod)
# [ ] HSTS enabled
# [ ] Certificate auto-renewal
```

### 5.2. Network Policies

```bash
# Проверить network policies
cat templates/networkpolicy.yaml
cat config/manifests/network-policies.yaml

# Checklist:
# [ ] Default deny ingress
# [ ] Explicit allow rules
# [ ] Egress restrictions (optional)
# [ ] Pod-to-pod communication restricted
```

### 5.3. Ingress Security Middlewares

```bash
# Проверить Traefik middlewares
cat templates/security-middlewares.yaml
grep -rn "middleware" templates/ingress*.yaml

# Checklist:
# [ ] Rate limiting middleware
# [ ] Security headers (X-Frame-Options, CSP, etc.)
# [ ] IP whitelist (для admin endpoints)
# [ ] Request size limits
```

---

## Шаг 6: Container Security Audit

### 6.1. Pod Security

```bash
# Проверить security contexts
grep -A20 "securityContext:" templates/deployment.yaml

# Checklist:
# [ ] runAsNonRoot: true
# [ ] readOnlyRootFilesystem: true (where possible)
# [ ] allowPrivilegeEscalation: false
# [ ] capabilities dropped
```

### 6.2. Image Security

```bash
# Проверить image references
grep -rn "image:" templates/*.yaml

# Checklist:
# [ ] Pinned versions (не :latest)
# [ ] Trusted registries
# [ ] Image scanning (в CI/CD)
# [ ] Minimal base images
```

---

## Шаг 7: Генерация отчёта

### 7.1. Findings Classification

| Severity | Criteria |
|---|---|
| 🔴 **Critical** | Remote code execution, auth bypass, data breach |
| 🟠 **High** | Privilege escalation, SQL injection, secrets exposure |
| 🟡 **Medium** | Missing security headers, weak TLS, logging PII |
| 🟢 **Low** | Best practice deviations, minor hardening |

### 7.2. Report Template

```markdown
# Security Audit Report — 

**Дата аудита:** YYYY-MM-DD
**Тип аудита:** [Quick scan / Standard / Deep dive]
**Scope:** [компоненты]

## Executive Summary

| Severity | Count |
|---|---|
| 🔴 Critical | N |
| 🟠 High | N |
| 🟡 Medium | N |
| 🟢 Low | N |

**Overall Risk Level:** [Critical / High / Medium / Low]

## Findings

### 🔴 Critical Findings

#### [CRIT-01] [Название]
- **Компонент:** [файл/модуль]
- **Описание:** [что нашли]
- **Impact:** [последствия эксплуатации]
- **Remediation:** [как исправить]
- **ADR-related:** [topic slug, если релевантно]

### 🟠 High Findings
...

### 🟡 Medium Findings
...

### 🟢 Low Findings
...

## Remediation Plan

| Priority | Finding | Owner | Deadline |
|---|---|---|---|
| P0 | CRIT-01 | | ASAP |
| P1 | HIGH-01 | | 7 days |
| P2 | MED-01 | | 30 days |

## ADR Compliance

| ADR Topic | Compliant | Notes |
|---|---|---|
| `${PLATFORM_SLUG}` | ✅/⚠️/❌ | |
| `unified-auth-architecture` | ✅/⚠️/❌ | |

## Next Steps
1. [Immediate actions]
2. [Short-term fixes]
3. [Long-term improvements]
```

---

## Шаг 8: ADR Update (если найдены архитектурные security gaps)

### 8.1. Когда создавать/обновлять ADR

| Находка | Действие |
|---|---|
| Новый security mechanism needed | Создать ADR |
| Существующий ADR не покрывает security | Обновить чеклист ADR |
| ADR-решение создаёт уязвимость | Предложить deprecation/update ADR |

### 8.2. Security-related ADR checklist items

При обновлении ADR добавить security-specific пункты:
```markdown
## Чеклист реализации

### Security (обязательные пункты)
- [ ] Secrets management: все credentials из env vars
- [ ] Input validation: все user inputs валидируются
- [ ] Auth: endpoint защищён authentication
- [ ] Authz: проверка permissions/roles
- [ ] Logging: security events логируются (без secrets)
- [ ] Rate limiting: защита от abuse
```

---

## Чеклист Security Audit

- [ ] Scope аудита определён
- [ ] Context7 запросы выполнены
- [ ] Authentication & Authorization проверены
- [ ] Secrets management проверен
- [ ] Database security проверена
- [ ] Payment security (${PAYMENT_PROVIDER}) проверена
- [ ] Network security проверена
- [ ] Container security проверена
- [ ] Findings классифицированы по severity
- [ ] Отчёт сгенерирован
- [ ] Remediation plan создан
- [ ] ADR обновлены (если требуется)

---

## Связанные промпты

| Промпт | Когда использовать |
|---|---|
| `promt-bug-fix.md` | Для исправления найденных уязвимостей |
| `promt-feature-add.md` | Для добавления security mechanisms |
| `promt-verification.md` | После remediation |

---

## Security Resources

| Resource | URL/Path |
|---|---|
| ${PAYMENT_PROVIDER} Security | `docs/official_document/${PAYMENT_PROVIDER_lower}/` |
| OWASP Top 10 | https://owasp.org/Top10/ |
| K8s Security | https://kubernetes.io/docs/concepts/security/ |
| CIS Benchmarks | https://www.cisecurity.org/benchmark/kubernetes |

---

## Журнал изменений

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.2 | 2026-03-06 | Добавлены секции Gate I: `## Быстрый старт`, `## Когда использовать`, `## Журнал изменений`. |
| 1.1 | 2026-02-25 | Добавлены `## Чеклист`, `## Связанные промпты`, Security Resources; unified Mission Statement. |
| 1.0 | 2026-02-24 | Первая версия: аудит безопасности с ${PAYMENT_PROVIDER} HMAC и K8s RBAC. |

---

**Prompt Version:** 1.2
**Date:** 2026-03-06
