---
# Generated from the docx in source/ by scripts/build_from_docx.py.
# Do not edit: change the Google Doc and re-export instead.
generated: true
---

# Guideline at a glance

<div class="px-disclaimer" markdown>
**Summary of the full guideline. If they differ, the full guideline applies.**
Every block below is quoted from the guideline and links to its source.
</div>

## What it is and who it is for

This guideline sets out an ethical framework and practical guidance for the responsible and trustworthy development and use of AI in Earth observation (EO), covering the whole lifecycle from data acquisition to model deployment and decision-making. It addresses the developers of foundation models (FMs) and agents, data and platform providers, the teams that apply models in operational or research use cases, and the bodies that review and oversee this work.

Version 0.1 (2026-11-02), the web version of deliverable D1.3.

Source: [Section 2 · Introduction](guideline/02-introduction.md)
{: .px-source }

## The 8 principles

- [**Transparency**](guideline/03-responsible-ai-principles.md#transparency): Transparency means that the data, models, assumptions and outputs of EO AI systems can be inspected and understood by the people who use or are affected by them.
- [**Fairness**](guideline/03-responsible-ai-principles.md#fairness): Fairness means that EO models and services do not systematically disadvantage regions, communities or user groups, and that no social group is stigmatised.
- [**Privacy**](guideline/03-responsible-ai-principles.md#privacy): Privacy means protecting personal and sensitive information throughout data collection, training, deployment and reporting.
- [**Robustness and Security**](guideline/03-responsible-ai-principles.md#robustness-and-security): Robustness is the ability of a model to keep performing reliably under noise, missing data, sensor changes and shifts in region, season or sensor.
- [**Uncertainty and Reliability**](guideline/03-responsible-ai-principles.md#uncertainty-and-reliability): This principle requires that model outputs come with a trustworthy indication of how far they can be relied upon.
- [**Energy Efficiency**](guideline/03-responsible-ai-principles.md#energy-efficiency): Energy efficiency, or green AI, addresses the environmental footprint of training and operating AI models.
- [**Human Oversight and Agency**](guideline/03-responsible-ai-principles.md#human-oversight-and-agency): Human oversight means that people remain able to understand, supervise and, where needed, override or stop AI systems and their outputs, and that responsibility for decisions stays with people rather than with the system.
- [**Social Impact**](guideline/03-responsible-ai-principles.md#social-impact): Social impact concerns the effects of EO AI services on people, institutions and society, and the human oversight needed to keep those effects beneficial.

Source: [Section 3 · Responsible AI Principles](guideline/03-responsible-ai-principles.md)
{: .px-source }

## Main foundation-model risks

- [**Hallucination**](guideline/04-foundation-model-risks.md#hallucination): Hallucination is the generation of content that is plausible but not supported by data or fact.
- [**Overfitting**](guideline/04-foundation-model-risks.md#overfitting): Overfitting occurs when a model fits its training distribution so closely that performance drops on new regions, seasons, sensors or events.
- [**Model Opacity**](guideline/04-foundation-model-risks.md#model-opacity): Model opacity is the difficulty of understanding why a large model produces a given output.
- [**Adversarial Attacks**](guideline/04-foundation-model-risks.md#adversarial-attacks): Adversarial attacks are deliberate manipulations that make a model fail or reveal protected information.
- [**Geoprivacy**](guideline/04-foundation-model-risks.md#geoprivacy): Geoprivacy is the protection of people and places from harm caused by locational information.
- [**Dual-Use**](guideline/04-foundation-model-risks.md#dual-use): Dual-use risk is the possibility that models and outputs built for civil EO services are used to cause harm, for example for surveillance, targeting or the profiling of vulnerable groups, or that capabilities developed for one purpose are repurposed for another.

Source: [Section 4 · Foundation Model Risks](guideline/04-foundation-model-risks.md)
{: .px-source }

## Risk tiers

| **Risk tier** | **Description** | **FM hallucination** |
|-----------------|----------------------|----------------------|
| **Low** | Limited consequences, with errors readily detectable and correctable. | An incorrect land-cover description in an exploratory application with no operational consequences. |
| **Medium** | Errors may affect analytical reliability, interpretation, or planning, but can be identified and corrected through validation. | An incorrect vegetation-change assessment influencing environmental monitoring results. |
| **High** | Errors could substantially affect safety, critical infrastructure, sensitive information, or consequential decisions. | Incorrectly identifying flood-exposed infrastructure during emergency response, potentially misleading operational decisions. |

Examples of tiers for PROTEUS models, datasets and use cases are collected in [Annex H · PROTEUS Risk-Tier Examples](guideline/20-annex-h-proteus-risk-tier-examples.md).

Source: [Section 4 · Foundation Model Risks](guideline/04-foundation-model-risks.md) · [Annex H · PROTEUS Risk-Tier Examples](guideline/20-annex-h-proteus-risk-tier-examples.md)
{: .px-source }

## Who does what

- Foundation model developers, meaning those who pretrain or fine-tune models, are responsible for meeting the requirements at each lifecycle stage and for submitting the compliance card and metadata.
- Data and platform providers are responsible for data documentation, privacy and geoprivacy screening, and the metadata infrastructure.
- Use case leads and deployers apply the guideline to their application, take part in its evaluation and report operational concerns.
- A responsible AI reviewer maintains the guideline, reviews submissions, advises developers and escalates unresolved findings.
- An independent advisory or ethics body reviews responsible AI integration and ethical concerns.

Source: [Section 2 · Introduction](guideline/02-introduction.md#roles-and-responsibilities) · [Annex F · PROTEUS Roles and Partner Mapping](guideline/18-annex-f-proteus-roles-and-partner-mapping.md)
{: .px-source }

## Must, should, may – and what changes in version 2

<div class="px-soon" markdown>
<span class="px-soon__tag">Coming soon</span> Definitions of must, should and may. This will be filled from [Annex D · Glossary](guideline/16-annex-d-glossary.md).
</div>

- It is the first of two versions: version 1 fixes documentation, data-level checks and minimum reporting, and version 2 adds automated validation once the validation tools have been tested on the first foundation models.
- The section includes a table that separates what is mandatory in this version (documentation, data-level checks and minimum reporting) from what is planned to become mandatory in version 2 once the validation tools have been tested on foundation models.

Source: [Annex D · Glossary](guideline/16-annex-d-glossary.md) · [Section 1 · Executive Summary](guideline/01-executive-summary.md) · [Section 11 · Automated Validation](guideline/11-automated-validation.md)
{: .px-source }

## Key obligations for builders

- Identify the requirements that apply to your role and lifecycle stage.

- Complete the compliance card at data collection, model training and release, with a justification and evidence for each parameter.

- Attach the machine-readable responsible AI metadata to every dataset and model you deliver.

- Report calibrated uncertainty, spatially blocked validation results and per-region performance with every model.

- Raise open issues with the responsible AI reviewer, through the escalation path, before release.

[Go to Quick tools :octicons-arrow-right-24:](tools/index.md){ .md-button .md-button--primary }

Source: [Section 1 · Executive Summary](guideline/01-executive-summary.md)
{: .px-source }

## Where to go next

<div class="grid cards" markdown>

-   :material-book-open-page-variant-outline:{ .lg } **The full guideline**

    ---

    Every section and annex, identical to deliverable D1.3.

    [:octicons-arrow-right-24: Read the guideline](guideline/index.md)

-   :material-hammer-wrench:{ .lg } **Quick tools**

    ---

    Building, training or releasing something? Checklists and forms.

    [:octicons-arrow-right-24: Open Quick tools](tools/index.md)

-   :material-earth:{ .lg } **Use cases**

    ---

    How the guideline applies to each PROTEUS use case.

    [:octicons-arrow-right-24: Browse use cases](tools/use-cases/index.md)

</div>
