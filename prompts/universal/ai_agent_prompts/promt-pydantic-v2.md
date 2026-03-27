# promt-pydantic-v2

## Назначение
Задает синтаксис Pydantic v2, использование computed_field, строгих типов и декораторов валидации.

## Когда использовать
- "pydantic", "model", "schema", "dto"
- Создание Pydantic моделей
- Миграция на Pydantic v2
- Валидация и сериализация данных

## Pydantic v2 основы

### Модель с типами
```python
from pydantic import BaseModel, Field, field_validator, computed_field
from typing import Optional
from datetime import datetime

class ItemModel(BaseModel):
    id: str
    name: str = Field(..., description="Имя элемента")
    description: Optional[str] = Field(None, description="Описание")
    created_at: datetime

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('name cannot be empty')
        return v
```

### Computed fields
```python
from pydantic import BaseModel, computed_field

class OrderModel(BaseModel):
    items: list[ItemModel]
    tax_rate: float = 0.1

    @computed_field  # @property в Pydantic v1
    @property
    def total(self) -> float:
        """Вычисляем общую сумму с налогом"""
        subtotal = sum(item.price for item in self.items)
        return subtotal * (1 + self.tax_rate)
```

### Валидация декораторы
```python
from pydantic import BaseModel, field_validator, model_validator

class UserModel(BaseModel):
    email: str
    age: int

    @field_validator('email')
    @classmethod
    def email_format(cls, v):
        if '@' not in v:
            raise ValueError('invalid email format')
        return v

    @model_validator(mode='after')
    @classmethod
    def check_age_consistency(cls, data):
        if data.age < 0 or data.age > 120:
            raise ValueError('age must be between 0 and 120')
        return data
```

## Миграция с Pydantic v1 на v2

### Основные изменения
- `@property` → `@computed_field`
- `@validator` → `@field_validator`
- Валидаторы модели → `@model_validator`
- `Optional` из `typing` → `Optional` из `pydantic`

### Шаблон миграции
```python
# Было (Pydantic v1)
from pydantic import BaseModel, validator

class OldModel(BaseModel):
    name: str

    @validator('name')
    def validate_name(cls, v):
        return v.strip()

# Стало (Pydantic v2)
from pydantic import BaseModel, field_validator

class NewModel(BaseModel):
    name: str

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        return v.strip()
```

## Лучшие практики

### 1. Использование Field
```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0, description="Цена в рублях")
    category: Optional[str] = Field(None, description="Категория продукта")
    in_stock: bool = Field(default=True, description="В наличии")
```

### 2. Config для модели
```python
from pydantic import ConfigDict

class User(BaseModel):
    username: str
    email: str

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid',  # или 'allow', 'ignore'
        json_schema_extra={
            'examples': [
                {'username': 'john_doe', 'email': 'john@example.com'}
            ]
        }
    )
```

### 3. Вложенные модели
```python
class Address(BaseModel):
    street: str
    city: str

class Person(BaseModel):
    name: str
    address: Address  # Вложенная модель

    @computed_field
    @property
    def full_address(self) -> str:
        return f"{self.address.street}, {self.address.city}"
```

### 4. Сериализация/Десериализация
```python
# JSON → Model
item = ItemModel(**json_data)

# Model → JSON
json_data = item.model_dump()
json_str = item.model_dump_json()

# Включение computed полей
json_with_computed = item.model_dump(mode='python')
```

## Примеры запросов

**"Создай Pydantic модель для пользователя"**:
```python
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password too weak')
        return v
```

**"Добавь валидацию для телефонного номера"**:
```python
from pydantic import BaseModel, field_validator
import re

class ContactForm(BaseModel):
    phone: str

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        pattern = r'^\+?[\d\s-]{10,15}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid phone format')
        return v
```

## Интеграция с FastAPI

```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ItemRequest(BaseModel):
    name: str
    price: float

@router.post("/items")
async def create_item(item: ItemRequest):
    """FastAPI автоматически валидирует через Pydantic"""
    # item уже проверен Pydantic
    return {"name": item.name, "price": item.price}
```

## Типы данных

### Примитивные типы
- `str`, `int`, `float`, `bool`
- `datetime`, `date`, `time`
- `bytes`, `decimal.Decimal`

### Коллекции
- `list[T]`, `set[T]`, `frozenset[T]`
- `dict[K, V]`, `tuple[T, ...]`

### Специальные типы
- `Optional[T]` — значение или None
- `Union[T1, T2]` — один из типов
- `Literal["a", "b"]` — фиксированные значения
- `EmailStr`, `HttpUrl`, `UUID`

### Generics
```python
from typing import Generic, TypeVar
from pydantic import BaseModel, GenericModel

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    data: T
    message: str = "success"
```

## Сhecklist для Pydantic v2
- [ ] Используются типы из `pydantic`, а не `typing`
- [ ] Валидаторы используют `@field_validator`
- [ ] Computed поля используют `@computed_field`
- [ ] Config использует `ConfigDict`
- [ ] JSON serialization через `model_dump()`
- [ ] Поддержка `model_dump_json()` для API
- [ ] Документация через `Field(description=...)`