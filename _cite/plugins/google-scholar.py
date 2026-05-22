import os
import re
from serpapi import GoogleSearch
from util import *


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

        # try to extract a citable DOI from the link (e.g. https://doi.org/10.xxxx/...)
        doi_match = re.search(r'doi\.org/(10\.[^\s&?#]+)', link)
        source_id = f"doi:{doi_match.group(1)}" if doi_match else ""

        # if no DOI found, leave id empty so cite.py keeps Scholar's metadata as-is
        # rather than passing a Scholar citation_id that Manubot cannot resolve
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

        # add source to list
        sources.append(source)

    return sources
