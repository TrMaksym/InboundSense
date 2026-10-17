import logging

import httpx
from lxml.parser import HTMLParser

logger = logging.getLogger(__name__)

HEADER = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        "AppleWebKit/537.36 (KHTML, like Gecko)"
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "uk-UA,uk;q=0.9,en;q=0.8"
}

UNWANTED_TAGS = [
    "script",
    "stype",
    "nav",
    "footer",
    "header",
    "noscript",
    "svg"
]

def extract_clean_text(html: str) -> str:
    tree = HTMLParser(html)
    for tag in UNWANTED_TAGS:
        for node in tree.css(tag):
            node.decompose()

    main_node = tree.css_first("article") or tree.css_first("main") or tree.css_first("body")
    if not main_node:
            return ""
    raw_text = main_node.text(separator=" ", strip=True)
    return " ".join(raw_text.split())

async def fetch_and_extract_text(url: str) -> str | None:
    try:
        async with httpx.AsyncClient(headers=HEADER, timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            return extract_clean_text(response.text)
    except httpx.HTTPError as e:
        logger.error(f"Error fetching URL: {url}", exc_info=True)
        return None










