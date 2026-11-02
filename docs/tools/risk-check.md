---
# Generated from the docx in source/ by scripts/build_from_docx.py.
# Do not edit: change the Google Doc and re-export instead.
generated: true
---

# Risk-tier self-check

Answer the questions below for the model, dataset, agent or output you are working on. The result is a suggested tier and what that tier triggers.

!!! warning "Indicative only – Draft – to be confirmed by the RAI lead"
    The result is indicative. The responsible AI reviewer decides the tier. Questions, logic and triggers are a draft derived from the tier descriptions in [Section 4 · Foundation Model Risks](../guideline/04-foundation-model-risks.md) and the reasons listed in [Annex H · PROTEUS Risk-Tier Examples](../guideline/20-annex-h-proteus-risk-tier-examples.md).

<div class="px-tool px-riskcheck" data-px-riskcheck>
<script type="application/json" data-px-data>{"status":"draft","note":"Draft – to be confirmed by the RAI lead","questions":[{"hint":"For example, wrongly identifying flood-exposed infrastructure during emergency response.","source":["risks"],"id":"safety","text":"Could an error substantially affect safety or critical infrastructure?","if_yes":"high","source_md":"[Section 4 · Foundation Model Risks](../guideline/04-foundation-model-risks.md)"},{"hint":"","source":["risks"],"id":"consequential","text":"Could an error substantially affect sensitive information or consequential decisions?","if_yes":"high","source_md":"[Section 4 · Foundation Model Risks](../guideline/04-foundation-model-risks.md)"},{"hint":"","source":["tiers"],"id":"vulnerable","text":"Do the outputs concern vulnerable populations or inform emergency response?","if_yes":"high","source_md":"[Annex H · PROTEUS Risk-Tier Examples](../guideline/20-annex-h-proteus-risk-tier-examples.md)"},{"hint":"For example, an incorrect vegetation-change assessment influencing environmental monitoring results.","source":["risks"],"id":"analysis","text":"Could an error affect analytical reliability, interpretation or planning?","if_yes":"medium","source_md":"[Section 4 · Foundation Model Risks](../guideline/04-foundation-model-risks.md)"},{"hint":"Low-tier errors are \"readily detectable and correctable\".","source":["risks","tiers"],"id":"detectable","text":"Would an error be hard to detect or to correct?","if_yes":"medium","source_md":"[Section 4 · Foundation Model Risks](../guideline/04-foundation-model-risks.md) · [Annex H · PROTEUS Risk-Tier Examples](../guideline/20-annex-h-proteus-risk-tier-examples.md)"},{"hint":"The degree of autonomy is one of the reasons for a tier.","source":["tiers"],"id":"autonomy","text":"Will outputs be used without a person checking them first?","if_yes":"medium","source_md":"[Annex H · PROTEUS Risk-Tier Examples](../guideline/20-annex-h-proteus-risk-tier-examples.md)"}],"tiers":{"low":{"description":"Limited consequences, with errors readily detectable and correctable.","example":"An incorrect land-cover description in an exploratory application with no operational consequences.","triggers":["Standard self-assessment with the compliance card"]},"medium":{"description":"Errors may affect analytical reliability, interpretation, or planning, but can be identified and corrected through validation.","example":"An incorrect vegetation-change assessment influencing environmental monitoring results.","triggers":["Validation to identify and correct errors before use"]},"high":{"description":"Errors could substantially affect safety, critical infrastructure, sensitive information, or consequential decisions.","example":"Incorrectly identifying flood-exposed infrastructure during emergency response, potentially misleading operational decisions.","triggers":["Mandatory human check before release","Escalation to the External Advisory Board where needed"]}},"tier_source":"[Section 4 · Foundation Model Risks](../guideline/04-foundation-model-risks.md)","examples_source":"[Annex H · PROTEUS Risk-Tier Examples](../guideline/20-annex-h-proteus-risk-tier-examples.md)"}</script>
<form class="px-questions" onsubmit="return false">

<fieldset class="px-question">
<legend>1. Could an error substantially affect safety or critical infrastructure?</legend>
<p class="px-question__hint">For example, wrongly identifying flood-exposed infrastructure during emergency response.</p>
<label><input type="radio" name="safety" value="yes"> Yes</label>
<label><input type="radio" name="safety" value="no"> No</label>
</fieldset>

<fieldset class="px-question">
<legend>2. Could an error substantially affect sensitive information or consequential decisions?</legend>

<label><input type="radio" name="consequential" value="yes"> Yes</label>
<label><input type="radio" name="consequential" value="no"> No</label>
</fieldset>

<fieldset class="px-question">
<legend>3. Do the outputs concern vulnerable populations or inform emergency response?</legend>

<label><input type="radio" name="vulnerable" value="yes"> Yes</label>
<label><input type="radio" name="vulnerable" value="no"> No</label>
</fieldset>

<fieldset class="px-question">
<legend>4. Could an error affect analytical reliability, interpretation or planning?</legend>
<p class="px-question__hint">For example, an incorrect vegetation-change assessment influencing environmental monitoring results.</p>
<label><input type="radio" name="analysis" value="yes"> Yes</label>
<label><input type="radio" name="analysis" value="no"> No</label>
</fieldset>

<fieldset class="px-question">
<legend>5. Would an error be hard to detect or to correct?</legend>
<p class="px-question__hint">Low-tier errors are &quot;readily detectable and correctable&quot;.</p>
<label><input type="radio" name="detectable" value="yes"> Yes</label>
<label><input type="radio" name="detectable" value="no"> No</label>
</fieldset>

<fieldset class="px-question">
<legend>6. Will outputs be used without a person checking them first?</legend>
<p class="px-question__hint">The degree of autonomy is one of the reasons for a tier.</p>
<label><input type="radio" name="autonomy" value="yes"> Yes</label>
<label><input type="radio" name="autonomy" value="no"> No</label>
</fieldset>

</form>
<div class="px-result" data-result aria-live="polite" hidden></div>
<button type="button" class="md-button" data-action="reset">Start again</button>
</div>

## The tiers

| Tier | Description (from the guideline) | What it triggers (draft) |
|------|----------------------------------|--------------------------|
| **Low** | Limited consequences, with errors readily detectable and correctable. | Standard self-assessment with the compliance card |
| **Medium** | Errors may affect analytical reliability, interpretation, or planning, but can be identified and corrected through validation. | Validation to identify and correct errors before use |
| **High** | Errors could substantially affect safety, critical infrastructure, sensitive information, or consequential decisions. | Mandatory human check before release; Escalation to the External Advisory Board where needed |

Source: [Section 4 · Foundation Model Risks](../guideline/04-foundation-model-risks.md) · [Annex H · PROTEUS Risk-Tier Examples](../guideline/20-annex-h-proteus-risk-tier-examples.md)
{: .px-source }

The questions and triggers live in `docs/data/risk_check.yml`, where the RAI lead can change them without touching code.
