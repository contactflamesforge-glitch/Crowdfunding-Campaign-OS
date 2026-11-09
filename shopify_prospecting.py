"""Public Shopify storefront prospect research helpers.

Signals are indicative only: a public storefront cannot reveal verified sales volume.
"""
import ipaddress
import re
import socket
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import requests


class StoreParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = []
        self.description = ""
        self.text = []
        self.links = []
        self.meta = {}
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag == "meta":
            key = (attrs.get("name") or attrs.get("property") or "").lower()
            if key in ("description", "og:description", "og:site_name"):
                self.meta[key] = attrs.get("content", "")
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        value = " ".join(data.split())
        if not value:
            return
        if self.in_title:
            self.title.append(value)
        self.text.append(value)


def _safe_public_url(raw_url):
    raw_url = (raw_url or "").strip()
    if not raw_url:
        raise ValueError("Enter a store URL.")
    if not re.match(r"^https?://", raw_url, re.I):
        raw_url = "https://" + raw_url
    parsed = urlparse(raw_url)
    if not parsed.hostname:
        raise ValueError("That URL is not valid.")
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(parsed.hostname, None)}
        for address in addresses:
            ip = ipaddress.ip_address(address)
            if not ip.is_global:
                raise ValueError("Private or local network addresses cannot be scanned.")
    except socket.gaierror:
        raise ValueError("The store domain could not be resolved.")
    return raw_url


def scan_store(raw_url):
    """Fetch a public storefront and extract lightweight, non-invasive signals."""
    url = _safe_public_url(raw_url)
    response = requests.get(
        url, timeout=18, allow_redirects=True,
        headers={"User-Agent": "CampaignOS-StoreResearch/1.0 (+public storefront review)"},
    )
    response.raise_for_status()
    if len(response.content) > 2_000_000:
        raise ValueError("Store page is larger than the 2 MB scan limit.")
    content_type = response.headers.get("content-type", "")
    if "html" not in content_type.lower():
        raise ValueError("The URL did not return an HTML storefront.")
    parser = StoreParser()
    parser.feed(response.text[:2_000_000])
    text = " ".join(parser.text)
    lower_html = response.text.lower()
    lower_text = text.lower()
    host = urlparse(response.url).hostname or ""
    shopify = any(signal in lower_html for signal in (
        "cdn.shopify.com", "shopify-section", "myshopify.com", "shopify.theme",
        "shopify-payment-button", "shopify-checkout-api-token"
    ))
    email_matches = sorted(set(re.findall(
        r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}", response.text, re.I
    )))
    emails = [e for e in email_matches if not any(x in e.lower() for x in (
        "example.com", "sentry.io", "wixpress.com", "shopify.com"
    ))][:12]
    links = [urljoin(response.url, link) for link in parser.links]
    link_text = " ".join(parser.links).lower() + " " + lower_text
    signals = {
        "reviews_visible": any(x in lower_text for x in ("reviews", "customer review", "★★★★★", "verified buyer")),
        "shipping_info": any(x in link_text for x in ("shipping", "delivery", "fulfillment")),
        "returns_info": any(x in link_text for x in ("return", "refund", "exchange")),
        "about_page": any(x in link_text for x in ("about", "our story")),
        "contact_page": any(x in link_text for x in ("contact", "mailto:")),
        "product_language": any(x in lower_text for x in ("add to cart", "add to bag", "buy now", "shop now")),
        "newsletter": any(x in lower_text for x in ("newsletter", "subscribe", "join our mailing")),
        "social_links": any(x in lower_text for x in ("instagram.com", "facebook.com", "tiktok.com", "pinterest.com")),
    }
    years = [int(y) for y in re.findall(r"(?:©|copyright|all rights reserved)[^0-9]{0,12}(20\\d{2})", lower_text)]
    current_year = 2026
    if years:
        latest_year = max(years)
        age_hint = "Established signal" if latest_year <= current_year - 2 else "Recent/current-year signal"
    else:
        latest_year = None
        age_hint = "Store age unclear"
    gaps = []
    for key, label in (
        ("reviews_visible", "No obvious customer-review proof found"),
        ("shipping_info", "Shipping/delivery information not obvious"),
        ("returns_info", "Returns/refund information not obvious"),
        ("about_page", "About/brand story not obvious"),
        ("contact_page", "Contact route not obvious"),
        ("product_language", "No obvious product purchase action found"),
    ):
        if not signals[key]:
            gaps.append(label)
    score = min(100, len(gaps) * 14 + (10 if not emails else 0))
    return {
        "url": response.url, "domain": host, "title": " ".join(parser.title)[:180] or parser.meta.get("og:site_name", host),
        "description": parser.meta.get("description") or parser.meta.get("og:description", ""),
        "is_shopify": shopify, "emails": emails, "signals": signals, "gaps": gaps,
        "store_age_hint": age_hint, "copyright_year": latest_year,
        "opportunity_score": score,
        "sales_status": "Potential conversion friction" if score >= 42 else "Insufficient public evidence",
        "evidence_note": "A public website scan cannot confirm whether a store makes sales or reveal revenue.",
    }
