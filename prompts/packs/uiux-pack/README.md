# UI/UX Pack

Интеграция UI/UX дизайн-системы в p9i.

## Структура

```
uiux-pack/
├── pack.json                    # Конфигурация с триггерами
├── prompts/
│   ├── promt-uiux-colors.md           # Цветовые палитры
│   ├── promt-uiux-typography.md       # Типографика
│   ├── promt-uiux-styles.md           # Визуальные стили
│   ├── promt-uiux-icons.md           # Иконки
│   ├── promt-uiux-tailwind.md        # TailwindCSS компоненты
│   ├── promt-uiux-shadcn.md          # shadcn/ui компоненты
│   ├── promt-uiux-textual.md         # Textual TUI
│   ├── promt-uiux-tauri.md           # Tauri desktop
│   └── promt-uiux-design-system.md   # Дизайн-система
└── data/
    └── uiux_reference.json           # 471 entry reference
```

## Триггеры p9i роутера

| Ключевое слово | Промпт |
|----------------|--------|
| `color`, `colors`, `palette` | promt-uiux-colors.md |
| `typography`, `font`, `fonts` | promt-uiux-typography.md |
| `style`, `glassmorphism`, `minimalism` | promt-uiux-styles.md |
| `icon`, `icons`, `iconset` | promt-uiux-icons.md |
| `tailwind`, `tailwindcss` | promt-uiux-tailwind.md |
| `shadcn`, `shadcn-ui` | promt-uiux-shadcn.md |
| `textual`, `tui`, `terminal` | promt-uiux-textual.md |
| `tauri`, `desktop`, `app` | promt-uiux-tauri.md |
| `design system`, `tokens` | promt-uiux-design-system.md |

## Использование

```bash
# Через p9i роутер
"Подбери цветовую палитру для SaaS. use p9i"
"Сгенерируй кнопку на Tailwind. use p9i"
"Создай дизайн-систему для e-commerce. use p9i"
```

## Reference Data

Датасет включает:
- **Colors**: 119 палитр для разных индустрий
- **Styles**: 103 визуальных стиля
- **Typography**: 74 шрифтовые пары
- **Icons**: 175 наборов иконок

## Версия

- **Pack**: 1.0.0
- **Reference Data**: 471 entries
- **Created**: 2026-03-24

## Лицензия

MIT License