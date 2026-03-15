#!/usr/bin/env python3

import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup


PROFILE_URL = "https://scholar.google.com/citations?user=NVSRY8kAAAAJ&hl=en"
SCHOLAR_URL = "https://scholar.google.com/citations?user=NVSRY8kAAAAJ&hl=en&view_op=list_works&sortby=pubdate"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def fetch_html() -> str:
    response = requests.get(SCHOLAR_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.text


def parse_publications(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("tr.gsc_a_tr")
    publications = []

    for row in rows[:5]:
      title_link = row.select_one("a.gsc_a_at")
      meta_lines = row.select("div.gs_gray")
      year_cell = row.select_one("span.gsc_a_h, span.gsc_a_y")

      if not title_link:
          continue

      href = title_link.get("href", "")
      if href.startswith("/"):
          href = f"https://scholar.google.com{href}"

      authors = normalize_whitespace(meta_lines[0].get_text(" ", strip=True)) if len(meta_lines) > 0 else ""
      venue = normalize_whitespace(meta_lines[1].get_text(" ", strip=True)) if len(meta_lines) > 1 else ""
      year = normalize_whitespace(year_cell.get_text(" ", strip=True)) if year_cell else ""

      if venue and year:
          venue = re.sub(rf"([,\s]+){re.escape(year)}$", "", venue).strip(" ,")

      publications.append(
          {
              "title": normalize_whitespace(title_link.get_text(" ", strip=True)),
              "url": href or SCHOLAR_URL,
              "authors": authors,
              "venue": venue,
              "year": year,
          }
      )

    return publications


def main() -> None:
    html = fetch_html()
    publications = parse_publications(html)

    output = {
        "source": "Google Scholar",
        "profile": PROFILE_URL,
        "updated_at": __import__("datetime").datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "publications": publications,
    }

    data_path = Path(__file__).resolve().parents[1] / "data" / "publications.json"
    data_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()