# Анализ ошибки: "p9i сгенерировал код, но не записал файлы"

## Симптомы

```
p9i generated code but didn't write files. Создаю структуру вручную.
```

## Корневые причины

### 1. Async/Sync Mismatch

```
p9i agent (async) → executor.execute() (await) → prompt.result() (sync) → файл не записан
```

**Решение**: Явный `await` на каждом уровне:
```python
result = await executor.execute(prompt, context)
await self._ensure_files_written(result)
```

### 2. Validation Gate Blocking Writes

```
LLM генерирует → валидация блокирует (не проходит regex/ast) → файлы не созданы
```

**Решение**: Pipeline с checkpoint:
```python
# Checkpoint-based pipeline
async def execute_with_checkpoint(self, prompt):
    result = await llm.generate(prompt)

    if not self._validate_result(result):
        logger.warning("Validation failed, using fallback")
        return await self._fallback_handler(result)

    # Save checkpoint before file write
    await self._save_checkpoint(result)

    await self._write_files(result)  # ← Critical: files written AFTER checkpoint
    return result
```

### 3. Validation Gate Blocking Writes

```
Agent генерирует код → валидация блокирует (не проходит regex/ast) → файлы не созданы
```

**Решение**: Pipeline с checkpoint:
```python
# Checkpoint-based pipeline
async def execute_with_checkpoint(self, prompt):
    result = await llm.generate(prompt)

    # Save checkpoint before file write
    await self._save_checkpoint(result)

    if not self._validate_result(result):
        logger.warning("Validation failed, attempting recovery")
        return await self._fallback_handler(result)

    await self._write_files(result)  # ← Critical: files written AFTER checkpoint
    return result
```

### 4. Graceful Shutdown (Drain) Issue

```
SIGTERM received → agent stopped mid-execution → files not flushed
```

**Решение**: Drain handler в executor:
```python
async def shutdown(self):
    logger.info("Draining in-flight tasks...")
    for task in self._in_flight:
        task.cancel()  # or await task.finish_gracefully()

    # Wait for flush
    await self._flush_buffers()

    logger.info("Shutdown complete")
```

## Архитектурные решения

### Option A: Checkpoint-Based Pipeline

```python
class CheckpointExecutor:
    async def execute(self, prompt: str, context: dict) -> ExecutionResult:
        # 1. Generate
        result = await self.llm.generate(prompt, context)

        # 2. Checkpoint BEFORE validation
        await self.checkpoint_manager.save(
            checkpoint_id=result.id,
            state=result.partial,
            phase="pre_validation"
        )

        # 3. Validate
        if not self.validator.validate(result):
            return await self._recover_from_checkpoint(result.id)

        # 4. Write files (after successful validation)
        await self.file_writer.write(result.files)

        # 5. Final checkpoint
        await self.checkpoint_manager.complete(result.id)

        return result
```

### Option B: Explicit File Write Tracking

```python
class FileTrackingExecutor:
    async def execute(self, prompt: str, context: dict) -> ExecutionResult:
        result = await self.llm.generate(prompt)

        # Track planned writes
        planned_writes = result.files.copy()

        # Validate
        if not self._validate(result):
            logger.error(f"Validation failed: {result.errors}")
            # Log but don't lose planned_writes for debugging
            await self._log_unwritten(planned_writes)
            raise ValidationError(result.errors)

        # Write with tracking
        written = await self._write_with_tracking(result.files)

        # Ensure all files written
        missing = set(planned_writes.keys()) - set(written.keys())
        if missing:
            logger.error(f"Files not written: {missing}")
            raise WriteError(missing)

        return result
```

### Option C: Two-Phase Commit

```python
class TwoPhaseCommitExecutor:
    async def execute(self, prompt: str, context: dict) -> ExecutionResult:
        # Phase 1: Generate + Validate (in-memory)
        result = await self.llm.generate(prompt)
        if not self.validator.validate(result):
            raise ValidationError(result.errors)

        # Phase 2: Write (durably)
        await self._write_files(result.files)

        # Verify all files exist
        await self._verify_files(result.files)

        return result
```

## Метрики для мониторинга

```python
class ExecutionMetrics:
    def __init__(self):
        self.generated_not_written = Counter("generated_not_written_total")
        self.validation_failures = Counter("validation_failures_total")
        self.write_failures = Counter("write_failures_total")
        self.checkpoint_recoveries = Counter("checkpoint_recoveries_total")
```

## Рекомендации

1. **Приоритет**: Checkpoint-based pipeline (Option A)
2. **Миграция**: Постепенная — добавить checkpoint в существующий executor
3. **Мониторинг**: Alert на `generated_not_written > 0`
4. **Testing**: Mock LLM, проверять что файлы реально записываются