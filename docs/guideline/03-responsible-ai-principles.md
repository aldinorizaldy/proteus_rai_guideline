---
# Generated from the docx in source/ by scripts/build_from_docx.py.
# Do not edit: change the Google Doc and re-export instead.
generated: true
---

# Responsible AI Principles

This section defines the eight principles that this guideline applies throughout the AI lifecycle. It gives definitions only: methods for meeting the principles are in the strategies section, and the specific risks of foundation models are in the risk section. The principles are transparency, fairness, privacy, robustness and security, uncertainty and reliability, energy efficiency, human oversight and agency, and social impact. Each principle is worded so that it can be turned into an evaluation criterion and an item in the self-assessment.

## Transparency

Transparency means that the data, models, assumptions and outputs of EO AI systems can be inspected and understood by the people who use or are affected by them. It covers documentation of datasets and models (provenance, intended use, limitations), disclosure that an output is AI-generated, openness about uncertainty, and explainability of model behaviour for non-expert users such as public authorities and service operators. Transparency is supported by the machine-readable RAI metadata and by the explainability strategy, and it is a condition for trust among institutional users, who may hesitate to adopt AI outputs without interpretability and clear uncertainty estimates.

## Fairness

Fairness means that EO models and services do not systematically disadvantage regions, communities or user groups, and that no social group is stigmatised. In Earth observation, unfairness mostly appears as geographic and demographic bias: uneven training data coverage across regions, climate zones or land cover types, uneven sensor availability, and differing accuracy across geographies. This subsection defines fairness for AI4EO and names the dimensions that are checked, such as accuracy gaps between regions, coverage bias in datasets, and equitable access to outputs for Entrusted Entities, SMEs and civil society. Methods for assessing and mitigating bias belong in the strategies section.

## Privacy

Privacy means protecting personal and sensitive information throughout data collection, training, deployment and reporting. In EO it includes data protection in the sense of the GDPR (minimisation, anonymisation, purpose limitation, security) and geo-privacy: protecting individuals, groups and sensitive sites from being identified or inferred from the location and content of satellite and in-situ data. The subsection also covers privacy risks of the models themselves, such as memorisation of training data and membership or attribute inference, and links to the privacy-preserving methods in the strategies section.

## Robustness and Security

Robustness is the ability of a model to keep performing reliably under noise, missing data, sensor changes and shifts in region, season or sensor. Security is its resistance to deliberate manipulation. This subsection defines both terms for AI4EO and FMs and covers natural perturbations such as cloud cover, atmospheric effects and sensor degradation, distribution shift across domains and time, adversarial examples, data and model poisoning, and the secure handling of training pipelines and model artefacts. It relates to the adversarial attack risk and to security by design in the pipelines that developers operate.

## Uncertainty and Reliability

This principle requires that model outputs come with a trustworthy indication of how far they can be relied upon. It distinguishes aleatoric uncertainty (irreducible noise in the data) from epistemic uncertainty (the model's lack of knowledge, which can be reduced and is most relevant for detecting operation outside the model's competence), and it requires uncertainty to be calibrated, meaning that stated confidence matches observed accuracy. Reliability additionally covers consistency of outputs, detection of out-of-distribution inputs, and a clear statement of the conditions under which a model has been validated. It is the basis for the uncertainty quantification strategy and for the communication of uncertainty to end users of EO services and agents.

## Energy Efficiency

Energy efficiency, or green AI, addresses the environmental footprint of training and operating AI models. This guideline applies the do no significant harm principle by optimising the energy-to-solution ratio of HPC training, using GPU-efficient training strategies, benchmarking improvements, reporting energy use openly and exploring renewable-powered HPC. This subsection defines the quantities to be reported (such as energy consumption, hardware and runtime, and emissions where they can be estimated), and the expectation that developers prefer parameter-efficient and reusable models where performance allows.

## Human Oversight and Agency

Human oversight means that people remain able to understand, supervise and, where needed, override or stop AI systems and their outputs, and that responsibility for decisions stays with people rather than with the system. It covers the level of autonomy given to a model or agent, the points in a workflow where a person must review, approve or reject an output before it is used, the information a person needs to exercise that control (uncertainty, limitations, provenance and conditions of validity), and the ability of affected users to question or contest a result. In Earth observation, oversight matters most where outputs feed time-critical or consequential decisions, such as emergency response, and where agents chain tools, models and data sources with little direct supervision. The level of oversight required scales with the severity and reversibility of the possible harm. This principle is put into practice through the human oversight strategy, the deployment and monitoring requirements, and the release decision rights in the governance section.

## Social Impact

Social impact concerns the effects of EO AI services on people, institutions and society, and the human oversight needed to keep those effects beneficial. It includes inclusiveness and accessibility, avoiding stigmatisation or disadvantage of any group, the sensitivity of use cases such as displacement monitoring and urban air quality, public acceptance, and the role of human-in-the-loop validation and participatory design with stakeholders. It also covers the use of social sciences and humanities methods to study how people and organisations adopt AI, and the ongoing review of ethical concerns by an independent advisory or ethics body.
