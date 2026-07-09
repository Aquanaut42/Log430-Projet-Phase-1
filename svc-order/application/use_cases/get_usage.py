# get_usage.py

import requests
import os
from domain.exceptions.order_exceptions import LineNotFound
from application.ports.order_repository import OrderRepository

class GetUsage:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def execute(self, customer_id: str) -> dict:

        line = self.repository.find_line_by_customer(customer_id)
        if not line:
            raise LineNotFound("Aucune ligne trouvée pour ce client")

        usage_data = self._fetch_usage(line.msisdn)

        return {
            "msisdn": line.msisdn,
            "plan_id": line.plan_id,
            "status": line.status.value,
            "usage": usage_data
        }

    def _fetch_usage(self, msisdn: str) -> dict:

        usage_url = os.getenv("USAGE_API_URL")
        try:
            response = requests.get(
                f"{usage_url}/usage/{msisdn}",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()

            return self._simulated_usage()
        except requests.exceptions.ConnectionError:
            return self._simulated_usage()

    def _simulated_usage(self) -> dict:

        return {
            "voix_minutes": 45,
            "sms": 120,
            "data_go": 3.2,
            "source": "simulé"
        }
