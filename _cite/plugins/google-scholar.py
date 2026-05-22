import os
import re
import json
from urllib.request import Request, urlopen
from urllib.parse import quote
from serpapi import GoogleSearch
from util import *


def _doi_from_crossref(title, authors):
    """Look up a DOI via CrossRef title search. Returns 'doi:...' or ''."""
    try:
        query = quote(title)
        url = f"https://api.crossref.org/works?query.title={query}&rows=1&select=DOI,title,author"
        headers = {
            "User-Agent": "gadani-lab-website/1.0 (https://github.com/Sachin-Gadani/gadani-lab-website; mailto:gadanis1@pitt.edu)"
        }
        req = Request(url=url, headers=headers)
        data = json.loads(urlopen(req, timeout=10).read())
        items = data.get("message", {}).get("items", [])
        if not items:
            return ""
        item = items[0]
        # Verify the title is a close match before trusting the DOI
        returned_title = " ".join(item.get("title", [""]))
        if normalize_title(returned_title) != normalize_title(title):
            return ""
        return f"doi:{item['DOI']}"
    except Exception:
        return ""


def normalize_title(title):
    """Lowercase, strip punctuation and extra spaces for comparison."""
    normalized = re.sub(r"[^\w\s]", "", title.lower())
    return " ".join(normalized.split())


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

    # query api
    @log_cache
    @cache.memoize(name=__file__, expire=1 * (60 * 60 * 24))
    def query(_id):
        params["author_id"] = _id
        return get_safe(GoogleSearch(params).get_dict(), "articles", [])

    response = query(_id)

    # list of sources to return
    sources = []

    # go through response and format sources
    for work in response:
        link = get_safe(work, "link", "")
        year = get_safe(work, "year", "")
        title = get_safe(work, "title", "")
        authors = list(map(str.strip, get_safe(work, "authors", "").split(",")))

        # 1. try doi.org link first (fast, no extra request)
        doi_match = re.search(r"doi\.org/(10\.[^\s&?#]+)", link)
        if doi_match:
            source_id = f"doi:{doi_match.group(1)}"
        else:
            # 2. fall back to CrossRef title lookup to get a citable DOI
            source_id = _doi_from_crossref(title, authors)

        source = {
            "id": source_id,
            "title": title,
            "authors": authors,
            "publisher": get_safe(work, "publication", ""),
            "date": (year + "-01-01") if year else "",
            "link": link,
        }

        # copy fields from entry to source
        source.update(entry)

        # add source to list
        sources.append(source)

    return sources
