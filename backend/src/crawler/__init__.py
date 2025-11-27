"""Crawler module for news website crawling and parsing.

This module provides an OOP framework for crawling news websites with:
- Abstract base class for extensibility
- Pydantic models for type safety
- Domain validation
- Concrete UDN crawler implementation

Example:
    >>> from src.crawler import UDNCrawler, DomainMismatchException
    >>> crawler = UDNCrawler()
    >>> headlines = crawler.get_headline("價格", page=1)
    >>> news = crawler.parse(headlines[0].url)
    >>> print(news.title, news.content)
"""

from .crawler_base import NewsCrawlerBase, Headline, News, NewsWithSummary
from .exceptions import DomainMismatchException
from .udn_crawler import UDNCrawler

__all__ = [
    "NewsCrawlerBase",
    "Headline",
    "News",
    "NewsWithSummary",
    "DomainMismatchException",
    "UDNCrawler",
]
