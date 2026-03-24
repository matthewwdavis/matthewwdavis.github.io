#!/usr/bin/env python3

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from scholarly import scholarly


SCHOLAR_ID = "NVSRY8kAAAAJ"
PROFILE_URL = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en"
MAX_PUBLICATIONS = 5


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


def main() -> None:
    publications = fetch_publications()

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