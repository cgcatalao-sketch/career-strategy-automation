# Methodology

## Purpose

This portfolio project demonstrates how a repeatable workflow can turn public job-market information into structured, traceable career decisions.

## Inputs

- An anonymised CSV containing job title, company, region, work mode and description.
- A JSON profile containing target roles, priority keywords, preferences and scoring weights.

## Scoring model

The fit score ranges from 0 to 100:

| Criterion | Weight | Logic |
|---|---:|---|
| Target-role match | 35 | The job title contains a configured target role. |
| Keyword coverage | 45 | Proportional coverage of the configured priority keywords. |
| Work-mode match | 15 | The work mode matches a configured preference. |
| Region match | 5 | The region matches a configured preference. |

The output preserves matched keywords and each component match. This makes the result explainable rather than presenting a score without evidence.

## Human review

The score supports prioritisation; it does not make an application decision. A person still validates job requirements, organisational context, eligibility and the quality of supporting evidence.

## Limitations

- The demonstration dataset is fictional and intentionally small.
- Phrase matching does not understand synonyms or context like a language model would.
- Scoring weights reflect a defined strategy and should be reviewed when priorities change.
- A high score is not a prediction of hiring success.

## Privacy

No applicant contact details, credentials, confidential employer information or private vacancy data are stored in this repository.
