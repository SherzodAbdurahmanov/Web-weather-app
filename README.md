# Прогноз погоды по городу

## Функциональность

- Поиск погоды по названию города
- [x] Читабельный вывод прогноза
- [ ] Автодополнение при вводе
- [ ] История поиска пользователя
- [ ] API с количеством запросов по городам
- [ ] Сохранение последнего запроса
- [ ] Docker
- [x] Тесты

## Технологии

- Backend: Django
- Frontend: HTML + TailwindCSS
- API: Open-Meteo

## Как запустить

```bash
git clone ...
cd weather-app
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
