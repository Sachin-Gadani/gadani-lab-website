"""
cite process to convert sources and metasources into full citations
"""

import traceback
from importlib import import_module
from pathlib import Path
from dotenv import load_dotenv
from util import *


# load environment variables
load_dotenv()


# save errors/warnings for reporting at end
errors = []
warnings = []

# output citations file
output_file = "_data/citations.yaml"


log()

log("Compiling sources")

# compiled list of sources
sources = []

# in-order list of plugins to run
plugins = ["google-scholar", "pubmed", "orcid", "sources"]

# loop through plugins
for plugin in plugins:
    # convert into path object
    plugin = Path(f"plugins/{plugin}.py")

    log(f"Running {plugin.stem} plugin")

    # get all data files to process with current plugin
    files = Path.cwd().glob(f"_data/{plugin.stem}*.*")
    files = list(filter(lambda p: p.suffix in [".yaml", ".yml", ".json"], files))

    log(f"Found {len(files)} {plugin.stem}* data file(s)", indent=1)

    # loop through data files
    for file in files:
        log(f"Processing data file {file.name}", indent=1)

        # load data from file
        try:
            data = load_data(file)
            # check if file in correct format
            if not list_of_dicts(data):
                raise Exception(f"{file.name} data file not a list of dicts")
        except Exception as e:
            log(e, indent=2, level="ERROR")
            errors.append(e)
            continue

        # loop through data entries
        for index, entry in enumerate(data):
            log(f"Processing entry {index + 1} of {len(data)}, {label(entry)}", level=2)

            # run plugin on data entry to expand into multiple sources
            try:
                expanded = import_module(f"plugins.{plugin.stem}").main(entry)
                # check that plugin returned correct format
                if not list_of_dicts(expanded):
                    raise Exception(f"{plugin.stem} plugin didn't return list of dicts")
            # catch any plugin error
            except Exception as e:
                # log detailed pre-formatted/colored trace
                print(traceback.format_exc())
                # log high-level error
                log(e, indent=3, level="ERROR")
                errors.append(e)
                continue

            # loop through sources
            for source in expanded:
                if plugin.stem != "sources":
                    log(label(source), level=3)

                # include meta info about source
                source["plugin"] = plugin.name
                source["file"] = file.name

                # add source to compiled list
                sources.append(source)

            if plugin.stem != "sources":
                log(f"{len(expanded)} source(s)", indent=3)

log("Merging sources by id")

def normalize_doi(doi_string):
    """Strip trailing single-digit version suffix from DOI (e.g. eLife .1, .2 versioning)"""
    if not doi_string or not doi_string.startswith("doi:"):
        return doi_string
    import re
    # Only strip 1-2 digit suffixes (version numbers); leave 3+ digit suffixes like .025 or .013
    return re.sub(r'\.\d{1,2}$', '', doi_string)

def normalize_title(title):
    """Normalize title for comparison"""
    if not title:
        return ""
    import re
    # Remove punctuation, lowercase, remove extra spaces
    normalized = re.sub(r'[^\w\s]', '', title.lower())
    normalized = ' '.join(normalized.split())
    return normalized

# First pass: merge by exact ID match
for a in range(0, len(sources)):
    a_id = get_safe(sources, f"{a}.id", "")
    if not a_id:
        continue
    for b in range(a + 1, len(sources)):
        b_id = get_safe(sources, f"{b}.id", "")
        if b_id == a_id:
            log(f"Found duplicate {b_id}", indent=2)
            sources[a].update(sources[b])
            sources[b] = {}

# Second pass: merge by normalized DOI (catches version differences)
for a in range(0, len(sources)):
    if not sources[a]:
        continue
    a_id = get_safe(sources, f"{a}.id", "")
    a_norm = normalize_doi(a_id)
    if not a_norm or not a_id.startswith("doi:"):
        continue
    
    for b in range(a + 1, len(sources)):
        if not sources[b]:
            continue
        b_id = get_safe(sources, f"{b}.id", "")
        b_norm = normalize_doi(b_id)
        
        if a_norm == b_norm and a_id != b_id:
            log(f"Found DOI version duplicate: {a_id} ≈ {b_id}", indent=2)
            # Keep the one with fewer version suffixes (usually the main DOI)
            if len(a_id) <= len(b_id):
                sources[a].update(sources[b])
                sources[b] = {}
            else:
                sources[b].update(sources[a])
                sources[a] = {}

# Third pass: merge by similar titles (catches preprint/published pairs)
for a in range(0, len(sources)):
    if not sources[a]:
        continue
    a_title = normalize_title(get_safe(sources, f"{a}.title", ""))
    if not a_title:
        continue
    
    for b in range(a + 1, len(sources)):
        if not sources[b]:
            continue
        b_title = normalize_title(get_safe(sources, f"{b}.title", ""))
        
        # Check if titles match and at least one author overlaps
        if a_title == b_title:
            a_authors = get_safe(sources, f"{a}.authors", [])
            b_authors = get_safe(sources, f"{b}.authors", [])
            
            # Simple overlap check
            if set(a_authors) & set(b_authors):
                a_id = get_safe(sources, f"{a}.id", "")
                b_id = get_safe(sources, f"{b}.id", "")
                log(f"Found title duplicate: {a_id} ≈ {b_id}", indent=2)
                
                # Prefer published DOI over preprint (not medRxiv/bioRxiv/openRxiv)
                if "10.1101" in b_id or "openrxiv" in b_id.lower():
                    sources[a].update(sources[b])
                    sources[b] = {}
                elif "10.1101" in a_id or "openrxiv" in a_id.lower():
                    sources[b].update(sources[a])
                    sources[a] = {}
                else:
                    # Both published, merge into first
                    sources[a].update(sources[b])
                    sources[b] = {}

sources = [entry for entry in sources if entry]

log(f"{len(sources)} total source(s) to cite")


log()

log("Generating citations")

# list of new citations
citations = []


# loop through compiled sources
for index, source in enumerate(sources):
    log(f"Processing source {index + 1} of {len(sources)}, {label(source)}")

    # if explicitly flagged, remove/ignore entry
    if get_safe(source, "remove", False) == True:
        continue

    # new citation data for source
    citation = {}

    # source id
    _id = get_safe(source, "id", "").strip()

    # Manubot doesn't work without an id
    if _id:
        log("Using Manubot to generate citation", indent=1)

        try:
            # run Manubot and set citation
            citation = cite_with_manubot(_id)

        # if Manubot cannot cite source
        except Exception as e:
            plugin = get_safe(source, "plugin", "")
            file = get_safe(source, "file", "")
            # if regular source (id entered by user), throw error
            if plugin == "sources.py":
                log(e, indent=3, level="ERROR")
                errors.append(f"Manubot could not generate citation for source {_id}")
            # otherwise, if from metasource (id retrieved from some third-party API), just warn
            else:
                log(e, indent=3, level="WARNING")
                warnings.append(
                    f"Manubot could not generate citation for source {_id} (from {file} with {plugin})"
                )
                # discard source from citations
                continue

    # preserve fields from input source, overriding existing fields
    citation.update(source)

    # ensure date in proper format for correct date sorting
    if get_safe(citation, "date", ""):
        citation["date"] = format_date(get_safe(citation, "date", ""))

    # add new citation to list
    citations.append(citation)


log()

log("Deduplicating citations by title")

# Plugin priority: lower = preferred (sources.py has user customizations like images)
_plugin_priority = {"sources.py": 0, "orcid.py": 1, "pubmed.py": 2, "google-scholar.py": 3}

def _citation_sort_key(cit):
    plugin = get_safe(cit, "plugin", "")
    _id = get_safe(cit, "id", "")
    is_preprint = "10.1101" in _id or "openrxiv" in _id.lower()
    return (1 if is_preprint else 0, _plugin_priority.get(plugin, 99))

def _last_names(authors):
    return {a.strip().split()[-1].lower() for a in authors if a.strip()}

title_seen = {}  # normalized title → index of kept citation
to_remove = set()

for i, cit in enumerate(citations):
    title = normalize_title(get_safe(cit, "title", ""))
    if not title:
        continue
    if title in title_seen:
        j = title_seen[title]
        kept = citations[j]
        my_last = _last_names(get_safe(cit, "authors", []))
        kept_last = _last_names(get_safe(kept, "authors", []))
        if my_last & kept_last:
            # Same paper: keep the higher-priority one
            if _citation_sort_key(cit) < _citation_sort_key(kept):
                to_remove.add(j)
                title_seen[title] = i
            else:
                to_remove.add(i)
    else:
        title_seen[title] = i

if to_remove:
    log(f"Removing {len(to_remove)} duplicate(s) by title", indent=1)

citations = [cit for i, cit in enumerate(citations) if i not in to_remove]

log()

log("Saving updated citations")


# save new citations
try:
    save_data(output_file, citations)
except Exception as e:
    log(e, level="ERROR")
    errors.append(e)


log()


# exit at end, so user can see all errors/warnings in one run
if len(warnings):
    log(f"{len(warnings)} warning(s) occurred above", level="WARNING")
    for warning in warnings:
        log(warning, indent=1, level="WARNING")

if len(errors):
    log(f"{len(errors)} error(s) occurred above", level="ERROR")
    for error in errors:
        log(error, indent=1, level="ERROR")
    log()
    exit(1)

else:
    log("All done!", level="SUCCESS")

log()
