"""Price service for fetching necessities price data."""

import json
import logging
from typing import Any, Optional

import requests
from fastapi import HTTPException

from src.config import settings

logger = logging.getLogger(__name__)


class PriceService:
    """Handles fetching price data from external API."""

    def __init__(self) -> None:
        """Initialize price service."""
        self.api_url = settings.necessities_price_api_url

    def get_necessities_prices(
        self, category: Optional[str] = None, commodity: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Get necessities prices from external API.

        Args:
            category: Optional category filter
            commodity: Optional commodity name filter

        Returns:
            List of price data

        Raises:
            HTTPException: If API request fails or returns invalid data
        """
        params = {"CategoryName": category, "Name": commodity}

        logger.info(f"Fetching necessities prices with params: {params}")

        try:
            response = requests.get(self.api_url, params=params, timeout=30)

            if response.status_code != 200:
                logger.error(
                    f"API returned status code {response.status_code}: {response.text}"
                )
                if response.status_code >= 500:
                    raise HTTPException(
                        status_code=502,
                        detail="The price data service is temporarily unavailable.",
                    )
                else:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Unable to retrieve price data (Error {response.status_code}).",
                    )

            if not response.content:
                logger.error("API returned empty response")
                raise HTTPException(
                    status_code=502,
                    detail="No price data was returned from the service. This might indicate the requested items are not available.",
                )

            try:
                data = response.json()
                logger.info(
                    f"Successfully fetched {len(data) if isinstance(data, list) else 'data'} from API"
                )
                return data
            except json.JSONDecodeError as e:
                logger.error(
                    f"Failed to decode JSON response: {e}. Response content: {response.text[:500]}"
                )
                raise HTTPException(
                    status_code=502,
                    detail="The price data service returned an invalid response format.",
                ) from e

        except requests.RequestException as e:
            logger.error(f"Request to external API failed: {e}")
            raise HTTPException(
                status_code=502, detail="Failed to retrieve price data."
            ) from e
