from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from .views import WeatherView


class WeatherViewTests(TestCase):
    def setUp(self):
        self.url = reverse('weather:home')

    def test_get_request_renders_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Прогноз погоды')

    @patch.object(WeatherView, 'fetch_coordinates')
    @patch.object(WeatherView, 'fetch_forecast')
    def test_valid_form_shows_forecast(self, mock_fetch_forecast, mock_fetch_coordinates):
        mock_fetch_coordinates.return_value = (55.75, 37.62)
        mock_fetch_forecast.return_value = {
            "time": ["2024-06-01"],
            "temperature_2m_min": [12.3],
            "temperature_2m_max": [24.7],
        }

        response = self.client.post(self.url, {'city': 'Москва'})
        self.assertEqual(response.status_code, 200)
        # Проверяем числа, а не символ "°"
        self.assertContains(response, '24.7')
        self.assertContains(response, '12.3')
        self.assertContains(response, 'Сб')

    @patch.object(WeatherView, 'fetch_coordinates')
    def test_city_not_found(self, mock_fetch_coordinates):
        mock_fetch_coordinates.return_value = None
        response = self.client.post(self.url, {'city': 'НесуществующийГород'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Город не найден')

    @patch.object(WeatherView, 'fetch_coordinates')
    @patch.object(WeatherView, 'fetch_forecast')
    def test_forecast_fetch_fail(self, mock_fetch_forecast, mock_fetch_coordinates):
        mock_fetch_coordinates.return_value = (55.75, 37.62)
        mock_fetch_forecast.return_value = None
        response = self.client.post(self.url, {'city': 'Москва'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Не удалось получить прогноз')

    def test_pick_icon_logic(self):
        view = WeatherView()
        build = view.build_forecast({
            "time": ["2024-06-01", "2024-06-02"],
            "temperature_2m_min": [20, 10],
            "temperature_2m_max": [30, 15],
        })

        self.assertEqual(build[0]["icon"], "sun")
        self.assertEqual(build[1]["icon"], "cloud-showers-heavy")
        self.assertEqual(build[0]["weekday"], "Сб")
        self.assertEqual(build[1]["weekday"], "Вс")
