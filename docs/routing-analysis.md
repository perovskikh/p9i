# Анализ архитектуры роутинга p9i

## Текущая архитектура

### 1. P9iRouter (точка входа)

```
User Request
     ↓
P9iRouter.route() → P9iRouter.classify()
     ↓
Intent (IntentType, agent_name, confidence)
     ↓
     ├─→ [confidence < 0.5] → CascadeRouter (fallback)
     │
     └─→ Processor (по IntentType)
            ├─→ CommandProcessor    → /help, /exit, /clear, /status
            ├─→ PromptCmdProcessor  → /prompt list, /prompt save
            ├─→ PackProcessor        → k8s-pack, ci-cd-pack
            ├─→ AgentTaskProcessor   → реализуй, спроектируй, проверь
            ├─→ NLQueryProcessor    → "покажи список", "что умеет"
            └─→ SystemProcessor      → "init p9i", "adapt to project"
```

### 2. AgentTaskProcessor → AgentRouter

```python
# AgentTaskProcessor.process()
orchestrator = get_orchestrator()
agents = router.detect_agents(request)  # ["developer"] или ["architect", "reviewer"]

for agent_name in agents:
    result = await orchestrator.execute_agent(agent_name, request)
```

### 3. AgentRouter (выбор агента)

```python
AgentRouter.detect_agents(request)
    ↓
Список агентов: ["migration", "full_cycle", "architect", "reviewer", "developer", "designer", "devops"]

# Примеры:
# "реализуй функцию" → ["full_cycle"] (если есть e2e)
# "спроектируй архитектуру" → ["architect"]
# "создай кнопку" → ["designer"]
```

### 4. AgentRouter.select_prompt() (выбор промта для агента)

```python
AgentRouter.select_prompt(agent_name, request)
    ↓
Agent.prompts = ["promt-feature-add", "promt-bug-fix", "..."]
    ↓
Выбор по ключевым словам:
    "добавь" → promt-feature-add
    "баг" → promt-bug-fix
    и т.д.
    ↓
Возвращает: prompt_name (строка, например "promt-feature-add")
```

### 5. Orchestrator.execute_agent()

```python
prompt_content = load_prompt(prompt_name)  # Читает .md файл
result = await executor.execute(prompt_content, context)
```

### 6. CascadeRouter (fallback)

```
CascadeRouter.route()
    ↓
RuleBasedRouter (confidence >= 0.9) - быстрый путь по ключевым словам
    ↓ (если не хватило)
SemanticRouter (confidence >= 0.7) - similarity по эмбеддингам
    ↓ (если не хватило)
LLMRouter - медленный AI путь
    ↓
PromptEntry (выбранный промт)
```

## Проблемы текущей архитектуры

### 1. **Дублирование логики**
- P9iRouter.classify() → Intent с agent_name
- AgentRouter.detect_agents() → список агентов (дублирует classify)

### 2. **CascadeRouter работает с PromptEntry, а не с агентами**
- CascadeRouter выбирает промт, а не агента
- Но в P9iRouter он используется как fallback для NL_QUERY
- Нет интеграции с AgentRouter

### 3. **AgentRouter.select_prompt() работает по устаревшей логике**
- Использует статический PROMPT_KEYWORDS словарь
- Не использует PromptRegistry из cascade
- Нет семантического поиска

### 4. **Два места выбора промта**
- AgentRouter.select_prompt() - для основного потока
- CascadeRouter - для fallback

## Рекомендуемая архитектура

```
User Request
     ↓
P9iRouter.classify() → Intent (agent_name, confidence)
     ↓
     ├─→ AgentRouter.select_prompt(agent_name, request)
     │         ↓
     │    PromptEntry (из PromptRegistry)
     │         ↓
     │    prompt_content = load_prompt(prompt.name)
     │         ↓
     │    executor.execute(prompt_content, context)
     │
     └─→ [низкая уверенность] → CascadeRouter.route()
                ↓
           PromptEntry (с большим候选池)
```

### Изменения:
1. **Убрать дублирование** - AgentRouter.detect_agents() использует результат P9iRouter.classify()
2. **Интегрировать PromptRegistry** - AgentRouter.select_prompt() использует PromptRegistry вместо статического словаря
3. **CascadeRouter как усилитель** - не заменяет AgentRouter, а улучшает выбор промта при низкой уверенности
4. **Один источник истины** - PromptRegistry единый для всех

## Вывод: правильно ли сейчас?

**Частично правильно:**
- ✅ P9iRouter правильно определяет IntentType
- ✅ AgentRouter правильно выбирает агента по ключевым словам
- ✅ CascadeRouter корректно работает как fallback

**Проблемы:**
- ❌ Дублирование между P9iRouter.classify() и AgentRouter.detect_agents()
- ❌ AgentRouter.select_prompt() не использует современный PromptRegistry
- ❌ Нет семантического поиска в AgentRouter - только статические keywords