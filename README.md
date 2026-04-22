# MVP файлообменник (Python + React)

Приложение позволяет:

- загружать файлы;
- проверять их на подозрительные признаки в фоне;
- сохранять метаданные и показывать алерты на фронтенде.

## Скачать проект

```bash
git clone https://github.com/sibeardev/karl.git
cd karl
```

## Переменные окружения

Перед запуском создайте файл `.env` в корне проекта и заполните его по примеру .env.dev:

```env
# Postgres
POSTGRES__USER=postgres
POSTGRES__PASSWORD=postgres
POSTGRES__DB=test
POSTGRES__HOST=backend-db
POSTGRES__PORT=5432

# Celery / Redis
REDIS__DSN=redis://backend-redis:6379/0

# Node.js
NEXT_TELEMETRY_DISABLED=0
PORT=3000
HOSTNAME="0.0.0.0"
```

## Запуск проекта

1. Поднять сервисы:

```bash
docker compose up --build
```

2. Применить миграции:

```bash
docker exec -it backend alembic upgrade head
```

## Доступ

- Фронтенд: `http://localhost:3000/test`
- Backend API docs: `http://localhost:8000/docs`
