---
# Generated from the docx in source/ by scripts/build_from_docx.py.
# Do not edit: change the Google Doc and re-export instead.
generated: true
---

# Responsible AI Metadata Schema

This section specifies the machine-readable responsible AI metadata that accompanies datasets, models and results. Its purpose is to move RAI documentation out of free text and into fields that pipelines can read, validate and aggregate. The schema covers three lifecycle stages (data collection, model training, and reporting or deployment) and records for each parameter a status, a justification and evidence. Dataset-level fields under consideration include checks on geoprivacy, coverage bias, consent basis, licence verification and personal-data scanning. The schema builds on existing metadata practice for FAIR principles and DCAT-AP, and one option is a dedicated extension of the STAC metadata standard. It is released in a machine-readable form (JSON) with versioning, because several teams will embed it in their pipelines.
