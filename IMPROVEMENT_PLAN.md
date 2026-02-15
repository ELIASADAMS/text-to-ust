# Анализ Проекта и План Улучшений

## Текущие Проблемы

### 1. **Монолит hiro_ust_dev.py (1349 строк)**
   - Содержит GUI, бизнес-логику, генератор UST всё в одном файле
   - Сложно тестировать отдельно
   - GUI запутана с логикой
   - **Решение**: Разделить на модули

### 2. **Лишние Файлы в Корне**
   - `archive/` - старый код (удалить)
   - `build/`, `build_opt/`, `dist/` - артефакты сборки (добавить в .gitignore)
   - `1x/`, `tests/` - неиспользуемые (удалить)
   - `Hiro_Main.cache/`, `Export/` - временные (удалить)
   - `*.spec` файлы - для PyInstaller (можно переместить в build/)
   - `criptshiro_ust_dev.py` - неправильное имя (удалить)

### 3. **Структура Данных Разнесена**
   - Все data модули в корне пакета
   - **Решение**: Создать подпакет `src/hiro_ust/data/`

### 4. **Отсутствует Слой API**
   - Нет возможности использовать библиотеку без GUI
   - **Решение**: Создать `core.py` с API

### 5. **Нет Логирования**
   - Ошибки скрыты в GUI
   - **Решение**: Добавить logger

## Предлагаемая Новая Структура

```
src/hiro_ust/
├── __init__.py                    # Package exports
├── core.py                         # Public API (NEW)
├── config.py                       # Config
├── constants.py                    # Constants
├── logger.py                       # Logging (NEW)
│
├── converter/                      # Phoneme & Text Conversion (NEW)
│   ├── __init__.py
│   ├── phonemizer.py              # ↔ moved from root
│   ├── hiragana_map.py            # ↔ moved from root
│   ├── kana_to_hiragana.py        # ↔ moved from root
│   └── mora_trie.py               # ↔ extracted from hiro_ust_dev
│
├── generator/                      # UST/USTX Generation (NEW)
│   ├── __init__.py
│   ├── ust_writer.py              # ↔ moved from root
│   ├── ustx_writer.py             # ↔ moved from root
│   ├── note_generator.py          # ↔ extracted from hiro_ust_dev
│   └── ust_strings.py             # ↔ moved from root
│
├── melody/                         # Melody Logic (NEW)
│   ├── __init__.py
│   ├── melody_logic.py            # ↔ existing
│   ├── scales.py                  # ↔ moved from root
│   ├── intone_utils.py            # ↔ moved from root
│   └── envelopes.py               # ↔ moved from root
│
├── voice/                          # Voice & Phonetic (NEW)
│   ├── __init__.py
│   ├── key_roots.py               # ↔ moved from root
│   ├── presets.py                 # ↔ moved from root
│   └── phonetic_utils.py          # ↔ NEW (extracted)
│
├── data/                           # Data tables
│   ├── __init__.py
│   ├── mora_trie_data.py          # ↔ moved from root
│   └── parts_presets.json         # ↔ moved from root
│
└── ui/                             # User Interface (NEW)
    ├── __init__.py
    ├── app.py                     # ↔ extracted from hiro_ust_dev
    ├── dialogs.py                 # ↔ NEW (file dialogs, etc)
    └── widgets.py                 # ↔ NEW (reusable UI components)
```

## Детальный План Рефакторинга

### Фаза 1: Создание Core API (NEW)

**src/hiro_ust/core.py** - Public interface для неGUI использования
```python
class HiroUSTProcessor:
    def process_lyrics(text, config) -> UST
    def generate_melody(phonemes, config) -> List[Note]
    def render_to_ust(notes, config) -> str
    def render_to_ustx(notes, config) -> str
```

**src/hiro_ust/logger.py** - Unified logging
```python
logger = get_logger(__name__)
logger.info/debug/warning/error
```

### Фаза 2: Создание Подпакетов

**src/hiro_ust/converter/** - Text/Phoneme conversion
- Содержит всю логику преобразования текста в фонемы
- Independent testing
- Reusable в других проектах

**src/hiro_ust/generator/** - UST/USTX generation
- Note generation logic
- Format writers
- Timing/envelope calculations

**src/hiro_ust/melody/** - Melody generation
- MelodyBrain
- Scale algorithms
- Accent handling

**src/hiro_ust/voice/** - Voice & prosody
- Key mappings
- Presets
- Voice-specific logic

**src/hiro_ust/data/** - Data tables
- Move all data tables here
- Easy to update

**src/hiro_ust/ui/** - GUI components
- Separate from logic
- Easy to replace/mock

### Фаза 3: Обновить Импорты

Все импорты обновить на новую структуру:
```python
from hiro_ust.core import HiroUSTProcessor
from hiro_ust.converter import Phonemizer, HiroUSTGenerator
from hiro_ust.generator import USTWriter, USTXWriter
from hiro_ust.melody import MelodyBrain, SCALES
```

## Файлы для Удаления

```
/archive/                    # Полностью удалить
/build/                      # Переместить в .gitignore
/build_opt/                  # Переместить в .gitignore  
/dist/                       # Переместить в .gitignore
/1x/                         # Удалить (дубликат assets)
/tests/                      # Если пусто, удалить
/Hiro_Main.cache/            # Временный файл
/Export/                     # Временный файл
/*.spec                      # Spec файлы (в .gitignore или build/)
/criptshiro_ust_dev.py       # Ошибка имени, удалить
/Hiro_Main.ust              # Временный файл
/.idea/                      # IDE кэш (в .gitignore)
/__pycache__/                # Python кэш (в .gitignore)
```

## Файлы для Создания

1. **src/hiro_ust/core.py** - Main API
2. **src/hiro_ust/logger.py** - Logging
3. **src/hiro_ust/converter/__init__.py** - Package
4. **src/hiro_ust/converter/mora_trie.py** - Extract from hiro_ust_dev
5. **src/hiro_ust/generator/__init__.py** - Package
6. **src/hiro_ust/generator/note_generator.py** - Extract note logic
7. **src/hiro_ust/melody/__init__.py** - Package reorganization
8. **src/hiro_ust/voice/__init__.py** - Package
9. **src/hiro_ust/voice/phonetic_utils.py** - Phonetic helpers
10. **src/hiro_ust/ui/__init__.py** - UI package
11. **src/hiro_ust/ui/app.py** - Extract GUI from hiro_ust_dev
12. **src/hiro_ust/ui/dialogs.py** - Dialog helpers
13. **src/hiro_ust/ui/widgets.py** - Reusable widgets

## Ожидаемые Улучшения

✅ **Модульность**: Каждый модуль отвечает за одно
✅ **Тестируемость**: Легко писать unit тесты  
✅ **Переиспользуемость**: Логика отделена от UI
✅ **Масштабируемость**: Легко добавлять новые форматы
✅ **Чистота**: Удалены все лишние файлы
✅ **Документация**: Ясная структура

## Примерный Объем Работы

- **Мин**: 2-3 часа (только структуризация)
- **Опт**: 4-5 часов (с экстракцией функций)
- **Макс**: 6-8 часов (с полной переписью + тесты)

## Рекомендуемый Порядок

1. ✓ Удалить лишние файлы/папки
2. ✓ Создать новую структуру папок
3. Переместить файлы в новые папки
4. Создать core.py с API
5. Добавить logger.py
6. Обновить импорты в __init__.py файлах
7. Рефакторить hiro_ust_dev.py → ui/app.py (большая работа)
8. Прогнать тесты
9. Обновить документацию

