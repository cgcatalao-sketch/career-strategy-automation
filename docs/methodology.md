# Methodology and privacy

## Purpose

This case study demonstrates how a repeatable workflow turns public vacancy information into structured, traceable market intelligence.

## Research snapshot

- Collection date: 23 August 2026.
- Sample: 40 representative public vacancies.
- Geography: Netherlands, Remote Europe/EMEA and selected global remote roles.
- Lenses: P1 Executive Assistance; P2 Business Support/Operations; P3 Project/Programme Support.

The sample supports market analysis; it is not presented as a list of 40 current application recommendations. Listings may change or expire after the collection date.

## Public input schema

Only seven fields are allowed in the public vacancy CSV: record ID, company, job title, broad location, work model, role family and recurring market keywords. A second public table contains record IDs and binary evidence for the 15 market capabilities. It contains no company name or personal assessment. The Python readers reject either file if an unexpected column appears. This makes privacy protection part of the executable workflow rather than a documentation promise alone.

## Analysis

The automation calculates:

- sample size;
- role-family distribution;
- work-model distribution;
- remote or remote-first count;
- occurrence and sample share of 15 market capabilities;
- three evidence-based positioning actions derived from the most frequent capabilities.

Every result can be traced to the public snapshot and capability configuration.

## Excluded private data

The repository intentionally excludes personal fit and language scores, application priority, eligibility risks, private assessments, recruiter contacts, application history, responses, salary notes, credentials and personally identifying information.

## Continuing discovery log

The historical 40-vacancy snapshot remains fixed so its results are reproducible. New strong opportunities found after the snapshot date are recorded separately in `discovered_opportunities.csv`. This preserves the original research baseline while demonstrating that monitoring continues to generate actionable outcomes. The public log contains professional match evidence and an official vacancy URL, but never private application status, answers, correspondence or documents.

## Human review

The findings support positioning and search-language decisions. They do not rank employers, predict hiring outcomes or replace human review of eligibility, organisational context and evidence quality.

## Limitations

- The 40-vacancy sample is directional rather than statistically representative of the entire labour market.
- Keyword matching cannot fully interpret synonyms or context.
- Public listings vary in detail and may change after collection.
- Capability frequency indicates advertised demand, not the relative importance of a skill inside an organisation.
