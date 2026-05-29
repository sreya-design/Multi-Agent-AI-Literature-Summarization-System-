import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict
import time
import random

ARXIV_API_URL = "http://export.arxiv.org/api/query"
NS = {"atom": "http://www.w3.org/2005/Atom"}


def search_arxiv(query: str, max_results: int = 8, retries: int = 5) -> List[Dict]:
    """Search ArXiv with retry/backoff logic for 429 rate limits."""
    params = urllib.parse.urlencode({
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    })
    url = f"{ARXIV_API_URL}?{params}"

    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 ArXivResearchBot/1.0 (research tool; polite)"
                }
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                xml_data = resp.read().decode("utf-8")
            break  # success

        except Exception as e:
            err = str(e).lower()
            is_rate_limit = "429" in err or "too many" in err or "unknown error" in err
            is_last = attempt == retries - 1

            if is_last:
                raise RuntimeError(f"ArXiv API request failed after {retries} attempts: {e}")

            if is_rate_limit:
                wait = 10 * (2 ** attempt) + random.uniform(1, 5)
            else:
                wait = 3 + random.uniform(0, 2)

            time.sleep(wait)

    root = ET.fromstring(xml_data)
    papers = []
    for entry in root.findall("atom:entry", NS):
        title_el = entry.find("atom:title", NS)
        summary_el = entry.find("atom:summary", NS)
        id_el = entry.find("atom:id", NS)
        published_el = entry.find("atom:published", NS)
        authors = [
            a.find("atom:name", NS).text
            for a in entry.findall("atom:author", NS)
            if a.find("atom:name", NS) is not None
        ]
        if title_el is None or summary_el is None:
            continue

        paper_id = id_el.text.strip() if id_el is not None else ""
        papers.append({
            "id": paper_id,
            "title": title_el.text.strip().replace("\n", " "),
            "abstract": summary_el.text.strip().replace("\n", " "),
            "authors": authors[:5],
            "published": published_el.text[:10] if published_el is not None else "Unknown",
            "url": paper_id,
        })

    time.sleep(3 + random.uniform(0, 2))  # polite delay between queries
    return papers


def deduplicate_papers(all_papers: List[Dict]) -> List[Dict]:
    """Remove duplicate papers by ArXiv ID."""
    seen = set()
    unique = []
    for p in all_papers:
        if p["id"] not in seen:
            seen.add(p["id"])
            unique.append(p)
    return unique
