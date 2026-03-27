# Pine Script v6 Pack

Интеграция Pine Script v6 для TradingView с полной документацией и промптами.

## Структура

```
pinescript-v6/
├── pack.json                    # Конфигурация с триггерами p9i
├── prompts/
│   ├── promt-pinescript-strategy.md    # Разработка стратегий
│   ├── promt-pinescript-indicator.md   # Индикаторы
│   ├── promt-pinescript-library.md     # Библиотеки (UDT, методы)
│   ├── promt-pinescript-debug.md       # Отладка
│   └── promt-pinescript-migrate.md     # Миграция v5→v6
└── data/
    └── pinescript_v6_reference.json    # 2666 строк reference
```

## Триггеры p9i роутера

| Ключевое слово | Промпт |
|----------------|--------|
| `pinescript`, `tradingview`, `индикатор` | promt-pinescript-indicator.md |
| `стратегия`, `strategy`, `торгов` | promt-pinescript-strategy.md |
| `library`, `библиотека` | promt-pinescript-library.md |
| `debug`, `отладка`, `баг` | promt-pinescript-debug.md |
| `миграция`, `v5 v6` | promt-pinescript-migrate.md |

## Использование

```bash
# Через p9i роутер
"Создай индикатор RSI для TradingView. use p9i"
"Напиши стратегию на пересечении MA. use p9i"
"Мигрируй код с v5 на v6. use p9i"
```

## Reference Data

Датасет включает:
- **Functions**: ta.sma(), ta.ema(), ta.rsi(), ta.macd(), ta.atr() и др.
- **Variables**: time, close, open, high, low, volume
- **Types**: User-Defined Types (UDT), series, const
- **Annotations**: //@version=6, indicator(), strategy(), library()
- **Drawing Objects**: line, label, box, table

## Версия

- **Pine Script**: v6
- **Pack**: 1.0.0
- **Data**: April 2025

## Лицензия

MIT License - based on TradingView documentation