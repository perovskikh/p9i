# DEPRECATED: Documentation Compression Executor

> **Статус:** DEPRECATED с 2026-03-07
> **Замена:** [`promt-documentation-quality-compression.md`](promt-documentation-quality-compression.md)

Этот промпт устарел и удалён из реестра. Используйте вместо него
`promt-documentation-quality-compression.md`.

**Причина депрекации:**
- Жёсткая цель «60%+ сокращения» создавала давление на агента
- Риск потери важной архитектурной информации ради достижения метрики
- Нет механизма защиты критического контента от сжатия

Новый промпт использует подход «качество > объём» с Protected Content Registry
и обязательным обоснованием каждого изменения.
