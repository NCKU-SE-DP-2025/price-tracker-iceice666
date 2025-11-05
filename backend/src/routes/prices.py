"""Price-related API endpoints."""

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query

from src.services.price_service import PriceService
from src.utils.dependencies import get_price_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/prices", tags=["prices"])


@router.get("/necessities-price")
def get_necessities_prices(
    category: Optional[str] = Query(None),
    commodity: Optional[str] = Query(None),
    price_service: PriceService = Depends(get_price_service),
) -> list[dict[str, Any]]:
    """Get necessities prices from external API.

    Args:
        category: Optional category filter
        commodity: Optional commodity name filter
        price_service: Price service

    Returns:
        List of price data

    Raises:
        HTTPException: If API request fails
    """
    return price_service.get_necessities_prices(category, commodity)
