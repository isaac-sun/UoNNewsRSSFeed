#!/usr/bin/env python3
"""Turn University of Nottingham student news into an RSS 2.0 feed.

Usage:
    pip install requests beautifulsoup4
    python uon_news_rss.py                       # all categories, first page
    python uon_news_rss.py --category academic --pages 2 --out academic.xml

Categories: all, academic, events, opportunities, research, sport,
            celebrations, support, uniNews, other
"""
import argparse
import datetime as dt
import re
import xml.etree.ElementTree as ET
from email.utils import format_datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://www.nottingham.ac.uk/currentstudents/news/news.aspx"
MONTHS = ("January|February|March|April|May|June|July|August|"
          "September|October|November|December")
DATE_RE = re.compile(rf"(\d{{1,2}} (?:{MONTHS}) \d{{4}})\s*$")
SKIP = ("news.aspx", "news-archive")


def scrape(category: str, pages: int) -> list[dict]:
    items, seen = [], set()
    headers = {"User-Agent": "Mozilla/5.0 (personal RSS feed generator)"}
    for page in range(pages):
        resp = requests.get(BASE, params={"category": category, "pageIndex": page},
                            headers=headers, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for a in soup.select('a[href*="/currentstudents/news/"]'):
            link = urljoin(BASE, a.get("href", ""))
            if any(s in link for s in SKIP) or link in seen:
                continue
            parts = list(a.stripped_strings)          # one string per inner element
            text = " ".join(parts)
            m = DATE_RE.search(text)
            if not parts or not m:
                continue                              # not a news card
            title = parts[0]
            # Title text may be glued to the date if the card has no inner markup
            title = DATE_RE.sub("", title).strip() or title
            summary = text[len(parts[0]):m.start()].strip()
            pub = dt.datetime.strptime(m.group(1), "%d %B %Y").replace(
                hour=9, tzinfo=dt.timezone.utc)
            seen.add(link)
            items.append({"title": title, "link": link,
                          "summary": summary, "date": pub})
    return items


def build_rss(items: list[dict], category: str) -> bytes:
    rss = ET.Element("rss", version="2.0")
    ch = ET.SubElement(rss, "channel")
    ET.SubElement(ch, "title").text = f"UoN Current Students News ({category})"
    ET.SubElement(ch, "link").text = f"{BASE}?category={category}"
    ET.SubElement(ch, "description").text = "University of Nottingham student news"
    ET.SubElement(ch, "lastBuildDate").text = format_datetime(
        dt.datetime.now(dt.timezone.utc))
    for it in items:
        e = ET.SubElement(ch, "item")
        ET.SubElement(e, "title").text = it["title"]
        ET.SubElement(e, "link").text = it["link"]
        ET.SubElement(e, "guid", isPermaLink="true").text = it["link"]
        ET.SubElement(e, "description").text = it["summary"]
        ET.SubElement(e, "pubDate").text = format_datetime(it["date"])
    ET.indent(rss)
    return ET.tostring(rss, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", default="all")
    ap.add_argument("--pages", type=int, default=1)
    ap.add_argument("--out", default="feed.xml")
    args = ap.parse_args()

    items = scrape(args.category, args.pages)
    if not items:
        raise SystemExit("No news items found - the page layout may have changed.")
    with open(args.out, "wb") as f:
        f.write(build_rss(items, args.category))
    print(f"Wrote {len(items)} items to {args.out}")
