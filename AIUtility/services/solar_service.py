import requests


class SolarService:

    BASE_URL = "https://re.jrc.ec.europa.eu/api/PVcalc"

    # --------------------------------------------------

    def get_solar_data(

        self,

        latitude,

        longitude,

        peak_power=1

    ):

        params = {

            "lat": latitude,

            "lon": longitude,

            "peakpower": peak_power,

            "loss": 14,

            "angle": 35,

            "aspect": 0,

            "outputformat": "json"

        }

        try:

            response = requests.get(

                self.BASE_URL,

                params=params,

                timeout=30

            )

            response.raise_for_status()

            return response.json()

        except Exception:

            return None

    # --------------------------------------------------

    def annual_generation(

        self,

        latitude,

        longitude,

        capacity_kw

    ):

        data = self.get_solar_data(

            latitude,

            longitude,

            capacity_kw

        )

        if data is None:

            return {

                "annual_energy": 0,

                "daily_energy": 0,

                "yearly_irradiance": 0,

                "daily_irradiance": 0

            }

        outputs = data.get(

            "outputs",

            {}

        )

        totals = outputs.get(

            "totals",

            {}

        )

        fixed = totals.get(

            "fixed",

            {}

        )

        return {

            "annual_energy":

                fixed.get("E_y", 0),

            "daily_energy":

                fixed.get("E_d", 0),

            "yearly_irradiance":

                fixed.get("H(i)_y", 0),

            "daily_irradiance":

                fixed.get("H(i)_d", 0)

        }

    # --------------------------------------------------

    def monthly_generation(

        self,

        latitude,

        longitude,

        capacity_kw

    ):

        data = self.get_solar_data(

            latitude,

            longitude,

            capacity_kw

        )

        if data is None:

            return []

        outputs = data.get(

            "outputs",

            {}

        )

        monthly = outputs.get(

            "monthly",

            {}

        ).get(

            "fixed",

            []

        )

        result = []

        for item in monthly:

            result.append({

                "month":

                    item.get(

                        "month",

                        0

                    ),

                "energy":

                    item.get(

                        "E_m",

                        0

                    ),

                "irradiance":

                    item.get(

                        "H(i)_m",

                        0

                    )

            })

        return result

    # --------------------------------------------------

    def roi(

        self,

        annual_energy,

        electricity_rate=8,

        installation_cost=60000,

        capacity_kw=5

    ):

        total_cost = installation_cost * capacity_kw

        annual_saving = annual_energy * electricity_rate

        payback = 0

        if annual_saving > 0:

            payback = total_cost / annual_saving

        return {

            "installation_cost":

                round(total_cost, 2),

            "annual_saving":

                round(annual_saving, 2),

            "payback":

                round(payback, 1),

            "profit_25_year":

                round(

                    annual_saving * 25 - total_cost,

                    2

                )

        }

    # --------------------------------------------------

    def carbon_offset(

        self,

        annual_energy

    ):

        return round(

            annual_energy * 0.82,

            2

        )

    # --------------------------------------------------

    def trees_equivalent(

        self,

        annual_energy

    ):

        return int(

            annual_energy / 21

        )