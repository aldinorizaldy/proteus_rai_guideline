---
title: Sample guideline (test fixture)
---

<!-- Test fixture for tests/test_build.py. Fictional content in the same
     structure as the real guideline, with the annexes filled in. Rebuild the
     docx with:  pandoc sample-guideline.md -o sample-guideline.docx -->

# Executive Summary

Sample teams should document their work at each lifecycle stage. It is the first of two versions: version 1 fixes documentation, and version 2 adds automated validation.

**What developers should do:**

- Identify the requirements that apply to your role.
- Complete the compliance card at each stage gate.

# Introduction

This sample guideline sets out sample guidance for testing. It addresses sample developers and sample reviewers.

## Roles and Responsibilities

This subsection defines who does what. Sample developers are responsible for the compliance card. A sample reviewer reviews submissions. Annex F maps these roles.

# Responsible AI Principles

This section defines two sample principles.

## Transparency

Transparency means that sample outputs can be inspected. More text follows.

## Fairness

Fairness means that sample models do not disadvantage regions.

# Foundation Model Risks

This section is a sample risk register.

## Hallucination

Hallucination is the generation of unsupported content.

| Risk tier | Description | Example |
|-----------|-------------|---------|
| Low | Limited consequences. | A demo map. |
| Medium | Errors may affect planning. | A monitoring product. |
| High | Errors could affect safety. | An emergency map. |

# Requirements by Lifecycle Stage

Requirements are listed per stage in Annex A.

# Compliance Assessment Process

The developer completes a compliance card at three lifecycle stages (data collection, model training, and reporting or deployment).

# Governance and Monitoring

Sample governance text.

# Annex A: Requirements Checklist

| ID | Requirement | Lifecycle stage | Responsible role | Binding level | Evidence | Use case |
|----|-------------|-----------------|------------------|---------------|----------|----------|
| DC-01 | Record the licence of every dataset. | Data collection | Data provider | must | Licence list | All |
| DC-02 | Screen imagery for sensitive locations. | Data collection | Data provider | must | Screening report | UC1 |
| TR-01 | Use spatially blocked validation. | Model training | FM developer | should | Validation report | UC1, UC2 |
| RE-01 | Publish calibrated uncertainty. | Release | FM developer | may | Calibration plot | UC2 |

# Annex B: Compliance Card and JSON Schema

| Stage | Parameter | Description | Allowed values |
|-------|-----------|-------------|----------------|
| Data collection | Licence verified | Every dataset licence is recorded. | yes, no, not applicable |
| Data collection | Geoprivacy screening | Imagery screened for sensitive sites. | yes, no |
| Model training | Spatial validation | Validation is spatially blocked. | |

# Annex D: Glossary

| Term | Definition |
|------|------------|
| must | A mandatory requirement. |
| should | A recommended requirement. |
| may | An optional requirement. |

# Annex E: Worked Example

## Step 1: Find the role

The sample developer identifies the role.

## Step 2: Fill in the compliance card

The developer completes the card for the data collection stage, see DC-01.

# Annex G: Use-Case Examples (UC1 to UC7)

This annex covers sample displacement monitoring (UC1) and sample crop stress (UC2).

## UC1 – Sample displacement monitoring

### Summary

UC1 maps sample settlements from imagery.

### Key principles and risks

Geoprivacy and social sensitivity.

### Requirements to watch

DC-02 and TR-01 need particular attention.

### Expected evidence

A geoprivacy screening report.

### Human oversight

An analyst reviews every map before release.

## UC2 – Sample crop stress

### Summary

UC2 detects sample crop stress.

### Requirements to watch

RE-01.

# Annex H: Risk-Tier Examples

| Use case | Example | Risk tier | Reasons | Review and oversight |
|----------|---------|-----------|---------|----------------------|
| UC1 | Settlement map | High | Concerns vulnerable populations. | Mandatory human check before release |
| UC2 | Crop stress index | Medium | Used for planning. | Validation before use |

# Annex L: Roadmap

This annex describes how this version develops into version 2 (M36). Audits are planned for M15 to M18.
