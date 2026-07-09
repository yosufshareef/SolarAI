from geopy.geocoders import Nominatim
from geopy.exc import (
    GeocoderTimedOut,
    GeocoderUnavailable,
    GeocoderServiceError
)


class MapService:

    def __init__(self):

        self.geocoder = Nominatim(

            user_agent="SolarTwinAI"

        )

    # --------------------------------------------------

    def search(self, query):

        if query is None:

            return None

        query = query.strip()

        if query == "":

            return None

        try:

            location = self.geocoder.geocode(

                query,

                timeout=10

            )

        except (

            GeocoderTimedOut,

            GeocoderUnavailable,

            GeocoderServiceError,

            Exception

        ):

            return None

        if location is None:

            return None

        return {

            "address": location.address,

            "lat": float(location.latitude),

            "lon": float(location.longitude)

        }