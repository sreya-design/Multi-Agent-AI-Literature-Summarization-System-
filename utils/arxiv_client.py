import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict
import time

ARXIV_API_URL = "http://export.arxiv.org/api/query"
NS = {"atom": "http://www.w3.org/2005/Atom"}

def search_arxiv(query: str, max_results: int = 8) -> List[Dict]:
    """Search ArXiv and return a list of paper dicts."""
    params = urllib.parse.urlencode({
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    })
    url = f"{ARXIV_API_URL}?{params}"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            xml_data = resp.read().decode("utf-8")
    except Exception as e:
        raise RuntimeError(f"ArXiv API request failed: {e}")

    root = ET.fromstring(xml_data)
    papers = []
    for entry in root.findall("atom:entry", NS):
        title_el = entry.find("atom:title", NS)
        summary_el = entry.find("atom:summary", NS)
        id_el = entry.find("atom:id", NS)
        published_el = entry.find("atom:published", NS)
        authors = [a.find("atom:name", NS).text for a in entry.findall("atom:author", NS) if a.find("atom:name", NS) is not None]

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
    time.sleep(0.5)  # Be respectful to ArXiv API
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
