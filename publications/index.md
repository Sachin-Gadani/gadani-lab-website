---
title: Publications
nav:
  order: 1
  tooltip: Published works
---

# {% include icon.html icon="fa-solid fa-microscope" %}Publications

{% include section.html %}

## Highlighted

<!--
  Highlighted citations are looked up by their DOI id (exact match) rather than
  by title. Title lookup uses a case-sensitive "contains" match, so a small
  difference in capitalization silently returns an empty citation. Using the id
  is unambiguous and avoids clashing with near-identical titles (e.g. the eLife
  paper vs. its openRxiv preprint).
-->

<!-- Autoimmune neuroinflammation leads to neuronal death via MIF nuclease-mediated parthanatos -->
{% include citation.html lookup="doi:10.1038/s41593-026-02201-7" style="rich" %}

<!-- Spatial Transcriptomics of Meningeal Inflammation ... Adjacent Brain Parenchyma -->
{% include citation.html lookup="doi:10.7554/eLife.88414.1" style="rich" %}

<!-- The Glia-Derived Alarmin IL-33 Orchestrates the Immune Response and Promotes Recovery following CNS Injury -->
{% include citation.html lookup="doi:10.1016/j.neuron.2015.01.013" style="rich" %}

<!-- note: to give a highlighted citation an image, add "image: images/<file>" to
     its entry in _data/sources.yaml (source of truth) and re-run the cite script.
     The generated _data/citations.yaml is what the page actually reads. -->

{% include section.html %}

## All

{% include search-box.html %}

{% include search-info.html %}

{% include list.html data="citations" component="citation" %}
