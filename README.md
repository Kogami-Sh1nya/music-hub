# Music Hub

Учебный музыкальный агрегатор: React + FastAPI + PostgreSQL + REST API. Аудиофайлы хранятся локально на backend, метаданные — в PostgreSQL.

## Возможности
- регистрация и вход по JWT;
- загрузка MP3/WAV/OGG/M4A;
- локальное хранение аудиофайлов;
- библиотека и поиск;
- избранное;
- создание плейлистов и добавление треков;
- рабочий HTML5-аудиоплеер с паузой, перемоткой и громкостью;
- адаптивный React-интерфейс на JSX/CSS + Bootstrap.

## 1. PostgreSQL
Создайте базу данных:

```sql
CREATE DATABASE music_hub;
```

По умолчанию backend использует:
`postgresql+psycopg2://postgres:postgres@localhost:5432/music_hub`

Если логин/пароль отличаются, задайте переменную `DATABASE_URL`.

## 2. Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgresql+psycopg://postgres:ВАШ_ПАРОЛЬ@localhost:5432/music_hub"
export SECRET_KEY="music-hub-secret"
uvicorn app.main:app --reload
```

API: http://localhost:8000
Swagger: http://localhost:8000/docs

Таблицы создаются автоматически при первом запуске.

## 3. Frontend
В другом терминале:

```bash
cd frontend
npm install
npm start
```

Откройте http://localhost:3000

Если backend находится по другому адресу, перед запуском задайте `REACT_APP_API_URL`.

## REST API
- `POST /api/auth/register` — регистрация
- `POST /api/auth/login` — вход
- `GET /api/tracks` — список/поиск треков
- `POST /api/tracks/upload` — загрузка аудио
- `GET /api/favorites` — избранное
- `POST /api/favorites/{track_id}` — добавить в избранное
- `DELETE /api/favorites/{track_id}` — удалить из избранного
- `GET /api/playlists` — плейлисты
- `POST /api/playlists` — создать плейлист
- `POST /api/playlists/{id}/tracks/{track_id}` — добавить трек

## Структура хранения
`backend/media/music/` — загруженные аудиофайлы.
PostgreSQL — пользователи, метаданные треков, избранное и плейлисты.
