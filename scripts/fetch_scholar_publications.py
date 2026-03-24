#!/usr/bin/env python3

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from scholarly import scholarly


SCHOLAR_ID = "NVSRY8kAAAAJ"
PROFILE_URL = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en"
MAX_PUBLICATIONS = 5
MAX_FETCH_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 10


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def fetch_publications() -> list[dict[str, str]]:
    author = scholarly.search_author_id(SCHOLAR_ID)
    author = scholarly.fill(author, sections=["publications"])

    publications = []
    for pub in author.get("publications", []):
        bib = pub.get("bib", {})
        title = normalize_whitespace(bib.get("title", ""))
        authors = normalize_whitespace(bib.get("author", ""))
        venue = normalize_whitespace(
            bib.get("venue", "") or bib.get("journal", "") or bib.get("booktitle", "")
        )
        year = str(bib.get("pub_year", ""))

        author_pub_id = pub.get("author_pub_id", "")
        if author_pub_id:
            url = (
                f"https://scholar.google.com/citations?view_op=view_citation"
                f"&hl=en&user={SCHOLAR_ID}&citation_for_view={author_pub_id}"
            )
        else:
            url = PROFILE_URL

        publications.append(
            {
                "title": title,
                "url": url,
                "authors": authors,
                "venue": venue,
                "year": year,
            }
        )

    # Return the 5 most recent publications sorted by year descending
    publications.sort(
        key=lambda p: int(p["year"]) if p["year"].isdigit() else 0,
        reverse=True,
    )
    return publications[:MAX_PUBLICATIONS]


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