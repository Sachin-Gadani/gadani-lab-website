import os
import re
import json
from urllib.request import Request, urlopen
from urllib.parse import quote
from serpapi import GoogleSearch
from util import *


# Map publisher URL patterns to Manubot-citable ids (no extra HTTP requests)
_LINK_ID_PATTERNS = [
    # Explicit doi.org redirect (most reliable)
    (r"doi\.org/(10\.[^\s&?#]+)", r"doi:\1"),
    # Nature (new-style article IDs)
    (r"nature\.com/articles/(s\d{5}-\d{3}-\d{5}-\d)", r"doi:10.1038/\1"),
    # Science
    (r"science\.org/doi/(10\.[^\s&?#]+)", r"doi:\1"),
    # PubMed
    (r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", r"pmid:\1"),
    # eLife (article number only in URL, reconstruct DOI)
    (r"elifesciences\.org/articles/(\d+)", r"doi:10.7554/eLife.\1"),
    # Generic: DOI embedded in URL path (Wiley, Sage, PNAS, BioMedCentral, preprints, etc.)
    (r"/(10\.\d{4,}/[^\s/?&#]+)", r"doi:\1"),
]


def _id_from_link(link):
    """Try to extract a Manubot-citable id from a publisher link."""
    for pattern, template in _LINK_ID_PATTERNS:
        match = re.search(pattern, link)
        if match:
            result = re.sub(pattern, template, match.group(0))
            # Strip preprint version suffixes (e.g. v2 at end of medRxiv/bioRxiv DOIs)
            result = re.sub(r'(doi:10\.1101/.+?)v\d+$', r'\1', result)
            return result
    return ""


def main(entry):
    """
    receives single list entry from google-scholar data file
    returns list of sources to cite
    """

    # get api key (serp api key to access google scholar)
    api_key = os.environ.get("GOOGLE_SCHOLAR_API_KEY", "")
    if not api_key:
        log('No "GOOGLE_SCHOLAR_API_KEY" env var, skipping Google Scholar', indent=2, level="WARNING")
        return []

    # serp api properties
    params = {
        "engine": "google_scholar_author",
        "api_key": api_key,
        "num": 100,  # max allowed
        "sortby": "pubdate",  # most recent first so new papers aren't missed
    }

    # get id from entry
    _id = get_safe(entry, "gsid", "")
    if not _id:
        raise Exception('No "gsid" key')

    # query api (cached 24 h)
    @log_cache
    @cache.memoize(name=__file__, expire=1 * (60 * 60 * 24))
    def query(_id):
        params["author_id"] = _id
        return get_safe(GoogleSearch(params).get_dict(), "articles", [])

    response = query(_id)

    # list of sources to return
    sources = []

    for work in response:
        link = get_safe(work, "link", "")
        year = get_safe(work, "year", "")
        title = get_safe(work, "title", "")
        authors = list(map(str.strip, get_safe(work, "authors", "").split(",")))

        # try to get a citable id from the link with no extra HTTP requests;
        # leave empty if none found so cite.py keeps Scholar metadata as-is
        source_id = _id_from_link(link)

        source = {
            "id": source_id,
            "title": get_safe(work, "title", ""),
            "authors": list(map(str.strip, get_safe(work, "authors", "").split(","))),
            "publisher": get_safe(work, "publication", ""),
            "date": (year + "-01-01") if year else "",
            "link": link,
        }

        # copy fields from entry to source
        source.update(entry)

        sources.append(source)

    return sources

