# Betting Platform

Реализованы два сервиса, две базы, Kafka как message brocker. 

**line-provider** - линия: события, коэффициент, дедлайн, завершение.  
**bet-maker** - ставки: приём, просмотр, закрытие.

Связь между сервисами: при ставке bet-maker асинхронно спрашивает line-provider, открыто ли событие. Когда оператор завершает событие, line-provider шлёт сообщение в Kafka, и bet-maker сам закрывает все pending-ставки по `event_id`.

---

## Стек

Python 3.10, FastAPI, SQLAlchemy 2 (async) + asyncpg, Alembic, aiokafka, httpx, pytest. 

Форматирование: black, isort, ruff. Задачи: invoke.

---

## Локальная разработка

### Требования

Python 3.10, Docker, Docker Compose.

### Окружение

```bash
git clone https://github.com/askel-io/betting_platform
cd betting_platform

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

cp .env.example .env
```


```bash
docker compose up --build
```

### Миграции

```bash
invoke migrate
```

### Проверка

```bash
curl http://localhost:8001/rest/api/v1/health
curl http://localhost:8000/rest/api/v1/health
```

---


## Архитектура
### Слои (в каждом сервисе)

```
src/
├── domain/           # сущности, бизнес-правила, интерфейсы репозиториев
├── application/      # use cases, DTO, порты
├── infrastructure/   # Postgres, Kafka, HTTP-клиенты
├── presentation/     # FastAPI, схемы, DI
└── errors/           # доменные исключения
```

Зависимости идут внутрь: presentatio -> application -> domain. Infrastructure реализует порты.

### Конфигурация

Единая точка - `config/settings.py` (pydantic-settings). Сервисные `infrastructure/config.py` - тонкие обёртки.

---


## Структура репозитория

```
betting_platform/
├── config/                 # общие настройки (.env)
├── line_provider/          # сервис линии
├── bet_maker/              # сервис ставок
├── tests/scenarios/        # scenario tests
├── docker-compose.yml
├── tasks.py
├── .env.example
└── pyproject.toml
```

---

## Разработка

```bash
invoke format          # isort + black
invoke lint            # ruff
invoke lint --fix
invoke check           # проверка без записи
invoke test            # pytest + coverage, 83 теста (покрытие 92%)
invoke migrate         # alembic upgrade head
```

Новая миграция:

```bash
cd line_provider   # или bet_maker
alembic revision --autogenerate -m "описание"
invoke migrate
```

---

## Тесты

83 теста в трёх слоях.

Перед сценариями:

```bash
docker compose up
invoke migrate
pytest test
```

---

## Что можно доработать

1. **Профит по ставке + payout.** При `PlaceBet` сохранять `coefficient` с line-provider, отдавать `profit` / `payout` в API.
3. **Reconciliation job.** Периодически искать `pending`-ставки по уже завершённым событиям - подстраховка на случай потери сообщения из Kafka.
4. **Outbox pattern** в line-provider вместо прямой отправки в Kafka.
