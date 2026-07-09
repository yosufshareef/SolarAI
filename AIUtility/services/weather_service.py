import requests


class WeatherService:

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    # --------------------------------------------------

    def get_weather(self, latitude, longitude):

        params = {

            "latitude": latitude,

            "longitude": longitude,

            "current": [

                "temperature_2m",

                "relative_humidity_2m",

                "apparent_temperature",

                "precipitation",

                "cloud_cover",

                "wind_speed_10m"

            ],

            "daily": [

                "sunrise",

                "sunset",

                "uv_index_max",

                "precipitation_sum"

            ],

            "timezone": "auto"

        }

        try:

            response = requests.get(

                self.BASE_URL,

                params=params,

                timeout=20

            )

            response.raise_for_status()

            return response.json()

        except Exception:

            return None

    # --------------------------------------------------

    def summary(self, latitude, longitude):

        data = self.get_weather(

            latitude,

            longitude

        )

        if data is None:

            return {

                "temperature": 0,

                "humidity": 0,

                "wind": 0,

                "cloud": 0,

                "rain": 0,

                "sunrise": "-",

                "sunset": "-",

                "uv": 0,

                "daily_rain": 0

            }

        current = data.get(

            "current",

            {}

        )

        daily = data.get(

            "daily",

            {}

        )

        return {

            "temperature":

                current.get(

                    "temperature_2m",

                    0

                ),

            "humidity":

                current.get(

                    "relative_humidity_2m",

                    0

                ),

            "wind":

                current.get(

                    "wind_speed_10m",

                    0

                ),

            "cloud":

                current.get(

                    "cloud_cover",

                    0

                ),

            "rain":

                current.get(

                    "precipitation",

                    0

                ),

            "sunrise":

                daily.get(

                    "sunrise",

                    ["-"]

                )[0],

            "sunset":

                daily.get(

                    "sunset",

                    ["-"]

                )[0],

            "uv":

                daily.get(

                    "uv_index_max",

                    [0]

                )[0],

            "daily_rain":

                daily.get(

                    "precipitation_sum",

                    [0]

                )[0]

        }

    # --------------------------------------------------

    def recommendation(self, weather):

        tips = []

        cloud = weather.get(

            "cloud",

            0

        )

        wind = weather.get(

            "wind",

            0

        )

        rain = weather.get(

            "daily_rain",

            0

        )

        uv = weather.get(

            "uv",

            0

        )

        if cloud < 30:

            tips.append(

                "Excellent solar conditions."

            )

        elif cloud < 60:

            tips.append(

                "Moderate cloud cover."

            )

        else:

            tips.append(

                "Heavy cloud cover may reduce generation."

            )

        if wind > 35:

            tips.append(

                "High wind speeds detected. Verify mounting structure."

            )

        if rain > 5:

            tips.append(

                "Rain forecast may naturally clean the panels."

            )

        if uv > 7:

            tips.append(

                "High UV index indicates strong solar potential."

            )

        if not tips:

            tips.append(

                "Weather conditions are within normal operating limits."

            )

        return tips