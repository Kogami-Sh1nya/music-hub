# Music Hub

Учебный музыкальный агрегатор: React + FastAPI + PostgreSQL + REST API. Аудиофайлы хранятся локально на backend, метаданные — в PostgreSQL.

## Возможности
- регистрация и вход по JWT;
- загрузка MP3/WAV/OGG/M4A;
- локальное хранение аудиофайлов;
- библиотека и поиск;
- избранное;
- создание и удаление плейлистов, добавление и удаление треков (в том числе кнопкой «в плейлист» у любого трека);
- теги у треков (жанры, настроения): задаются при загрузке и редактируются позже, страница «Теги» с фильтром по тегу;
- рекомендации на главной: подборка по самым часто прослушиваемым тегам и авторам;
- профиль: статистика прослушиваний, любимые теги и авторы, недавно прослушанное, смена пароля, очистка истории;
- раздел «Авторы»: список исполнителей и страница автора со всеми его треками;
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

Таблицы создаются автоматически при первом запуске. При обновлении с прошлой версии новые таблицы (`tags`, `track_tags`, `listens`) создадутся сами при перезапуске backend, существующие данные не меняются.

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
- `DELETE /api/playlists/{id}` — удалить плейлист
- `POST /api/playlists/{id}/tracks/{track_id}` — добавить трек
- `DELETE /api/playlists/{id}/tracks/{track_id}` — убрать трек из плейлиста
- `GET /api/tracks?search=...&tag=...` — поиск (по названию, автору, альбому, тегам) и фильтр по тегу
- `PUT /api/tracks/{id}/tags` — заменить теги трека, тело: `{"tags": ["рок", "грустное"]}`
- `POST /api/tracks/{id}/listen` — записать прослушивание (нужно для рекомендаций)
- `GET /api/tags` — все теги с количеством треков
- `GET /api/authors` — список авторов
- `GET /api/authors/detail?name=...` — автор и его треки
- `GET /api/recommendations` — подборка по истории прослушиваний
- `GET /api/profile` — данные и статистика профиля
- `PUT /api/profile/password` — сменить пароль, тело: `{"old_password": "...", "new_password": "..."}`
- `DELETE /api/profile/history` — очистить историю прослушиваний

## Демо-музыка
В `backend/demo_music` лежат 9 оригинальных инструментальных треков (синтезированы кодом, лицензия CC0 — можно использовать свободно).
Добавить их в приложение (из папки `backend`, после первого запуска сервера):

```bash
python seed_demo.py            # добавить демо-треки с авторами и тегами
python seed_demo.py --remove   # удалить их
```

## Структура хранения
`backend/media/music/` — загруженные аудиофайлы.
PostgreSQL — пользователи, метаданные треков, теги, история прослушиваний, избранное и плейлисты.
