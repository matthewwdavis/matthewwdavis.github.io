#!/usr/bin/env python3

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests
from scholarly import scholarly


SCHOLAR_ID = "NVSRY8kAAAAJ"
PROFILE_URL = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en"
MAX_PUBLICATIONS = 5
MAX_FETCH_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 10
DOI_PATTERN = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
MONTH_NAMES = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalize_month(value: str | int | None) -> str:
    if value is None:
        return ""

    if isinstance(value, int):
        return MONTH_NAMES.get(value, "")

    text = normalize_whitespace(str(value))
    if not text:
        return ""

    if text.isdigit():
        return MONTH_NAMES.get(int(text), "")

    # Keep text month names like "Jan" or "January".
    return text


def extract_doi(bib: dict[str, str], pub_url: str) -> str:
    bib_doi = normalize_whitespace(str(bib.get("doi", "")))
    if bib_doi:
        return bib_doi

    for source in (pub_url, str(bib.get("citation", ""))):
        match = DOI_PATTERN.search(source)
        if match:
            return match.group(0)

    return ""


def get_month_from_crossref(doi: str) -> str:
    if not doi:
        return ""

    try:
        response = requests.get(
            f"https://api.crossref.org/works/{quote(doi, safe='')}",
            headers={"User-Agent": "PublicationFetcher/1.0 (mailto:contact@example.com)"},
            timeout=15,
        )
        response.raise_for_status()
        message = response.json().get("message", {})
        date_parts = message.get("issued", {}).get("date-parts", [])
        if date_parts and len(date_parts[0]) >= 2:
            return normalize_month(date_parts[0][1])
    except Exception:
        return ""

    return ""


def fetch_publications() -> list[dict[str, str]]:
    author = scholarly.search_author_id(SCHOLAR_ID)
    author = scholarly.fill(author, sections=["publications"])

    publication_summaries = sorted(
        author.get("publications", []),
        key=lambda pub: int(str(pub.get("bib", {}).get("pub_year", "0")) or "0"),
        reverse=True,
    )[:MAX_PUBLICATIONS]

    publications = []
    for pub in publication_summaries:
        filled_pub = scholarly.fill(pub)
        bib = filled_pub.get("bib", {})
        title = normalize_whitespace(bib.get("title", ""))
        authors = normalize_whitespace(bib.get("author", ""))
        venue = normalize_whitespace(
            bib.get("venue", "") or bib.get("journal", "") or bib.get("booktitle", "")
        )
        year = str(bib.get("pub_year", ""))
        month = normalize_month(bib.get("month"))

        pub_url = filled_pub.get("pub_url", "")
        doi = extract_doi(bib, pub_url)
        if not month:
            month = get_month_from_crossref(doi)

        author_pub_id = filled_pub.get("author_pub_id", "")
        if author_pub_id:
            url = (
                f"https://scholar.google.com/citations?view_op=view_citation"
                f"&hl=en&user={SCHOLAR_ID}&citation_for_view={author_pub_id}"
            )
        elif pub_url:
            url = pub_url
        else:
            url = PROFILE_URL

        publications.append(
            {
                "title": title,
                "url": url,
                "authors": authors,
                "venue": venue,
                "month": month,
                "year": year,
            }
        )

    return publications


def fetch_publications_with_retries() -> list[dict[str, str]]:
    last_error: Exception | None = None

    for attempt in range(1, MAX_FETCH_ATTEMPTS + 1):
        try:
            publications = fetch_publications()
            if not publications:
                raise RuntimeError("No publications returned from Google Scholar")
            return publications
        except Exception as error:
            last_error = error
            if attempt == MAX_FETCH_ATTEMPTS:
                break
            print(
                f"Fetch attempt {attempt}/{MAX_FETCH_ATTEMPTS} failed: {error}. "
                f"Retrying in {RETRY_DELAY_SECONDS}s..."
            )
            time.sleep(RETRY_DELAY_SECONDS)

    raise RuntimeError(
        f"Failed to fetch publications after {MAX_FETCH_ATTEMPTS} attempts"
    ) from last_error


def main() -> None:
    publications = fetch_publications_with_retries()

    output = {
        "source": "Google Scholar",
        "profile": PROFILE_URL,
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "publications": publications,
    }

    data_path = Path(__file__).resolve().parents[1] / "data" / "publications.json"
    data_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()