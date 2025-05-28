from django.views.generic import FormView
from .forms import CityForm
from datetime import datetime
import httpx


class WeatherView(FormView):
    """
    View-класс для отображения формы поиска города
    и показа прогноза погоды по введённому городу.
    """
    template_name = 'weather/weather_form.html'
    form_class = CityForm

    def form_valid(self, form):
        """
        Обрабатывает валидную форму:
        - Получает координаты города
        - Получает прогноз погоды
        - Формирует данные и передаёт в шаблон
        """
        city = form.cleaned_data['city']
        coords = self.fetch_coordinates(city)

        if not coords:
            return self.render_error(form, "Город не найден")

        forecast_data = self.fetch_forecast(*coords)
        if not forecast_data:
            return self.render_error(form, "Не удалось получить прогноз")

        forecast = self.build_forecast(forecast_data)
        return self.render_to_response({
            'form': form,
            'city': city,
            'forecast': forecast,
        })

    def fetch_coordinates(self, city_name: str) -> tuple[float, float] | None:
        """
        Делает запрос к Open-Meteo Geocoding API,
        чтобы получить координаты (широту и долготу) по названию города.
        Возвращает (lat, lon) или None при ошибке.
        """
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=ru&format=json"
        try:
            response = httpx.get(url, timeout=5)
            data = response.json()
            result = data.get("results", [{}])[0]
            return result["latitude"], result["longitude"]
        except (KeyError, IndexError, httpx.RequestError):
            return None

    def fetch_forecast(self, lat: float, lon: float) -> dict | None:
        """
        Делает запрос к Open-Meteo Forecast API,
        чтобы получить прогноз погоды по координатам.
        Возвращает словарь с данными прогноза или None при ошибке.
        """
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&daily=temperature_2m_max,temperature_2m_min"
            f"&timezone=auto"
        )
        try:
            response = httpx.get(url, timeout=5)
            return response.json().get("daily")
        except httpx.RequestError:
            return None



    def build_forecast(self, data: dict) -> list[dict]:
        """
         Добавляет иконку погоды по температуре и дни недели.
        """
        def pick_icon(t_min, t_max):
            avg = (t_min + t_max) / 2
            if avg >= 27:
                return "sun"
            elif avg >= 23:
                return "cloud-sun"
            else:
                return "cloud-showers-heavy"

        days_ru = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

        return [
            {
                "date": date,
                "min": round(t_min, 1),
                "max": round(t_max, 1),
                "icon": pick_icon(t_min, t_max),
                "weekday": days_ru[datetime.strptime(date, "%Y-%m-%d").weekday()]
            }
            for date, t_min, t_max in zip(
                data["time"], data["temperature_2m_min"], data["temperature_2m_max"]
            )
        ]

    def render_error(self, form, message: str):
        """
        Отображает шаблон с сообщением об ошибке.
        Используется при ошибке геокодинга или получения прогноза.
        """
        return self.render_to_response({
            'form': form,
            'error': message
        })
