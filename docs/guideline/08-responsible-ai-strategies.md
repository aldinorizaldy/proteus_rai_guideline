---
# Generated from the docx in source/ by scripts/build_from_docx.py.
# Do not edit: change the Google Doc and re-export instead.
generated: true
---

# Responsible AI Strategies

This section turns the principles and risks into practice. Where the principles and risk sections say what is required and why, the strategies describe how developers can meet the requirements, with method options, guidance on choosing between them, and a minimum reporting requirement. The strategies are designed to be model-agnostic, so that they apply whoever develops a given FM, and they connect to the automated validation section. Each strategy is mapped to the principles and risks it addresses.

## Uncertainty Quantification

This strategy covers how to quantify and communicate uncertainty and how to verify that it is calibrated, and it supports the principle of uncertainty and reliability. It separates aleatoric from epistemic uncertainty and presents the main method families: approximate Bayesian methods (MC Dropout, Bayesian neural networks, Laplace approximation, SWAG), ensembles (deep, snapshot and batch ensembles), single-pass evidential methods (evidential deep learning and deep evidential regression, which can be overconfident on out-of-distribution inputs and must be tested), post-hoc calibration (temperature scaling, Platt and isotonic scaling), and conformal prediction (split conformal, conformalised quantile regression, and adaptive or online variants for drift over the forecast horizon). Out-of-distribution and novelty detection complement these methods but do not replace them. Because EO samples are spatially autocorrelated, calibration and test sets should be spatially blocked; otherwise the exchangeability assumption of conformal prediction is violated. Minimum reporting: the method family and the uncertainty type addressed, a calibration metric (ECE for classification, CRPS or PICP for regression), the coverage level where conformal prediction is used, and known limitations.

## Explainability

This strategy covers methods that make model behaviour understandable to developers, auditors and users. It supports the transparency principle and addresses model opacity. It describes feature-attribution and saliency methods, attention and concept-based analysis, example-based explanations and, for language-based agents, grounding and traceable reasoning, with guidance on which suit pixel-level, time-series and multimodal models and which work with only input and output access. It also covers sanity checks that test whether an explanation is faithful to the model, and how explanations are presented to non-expert users of EO services and agents. Minimum reporting: the method used, the model and task it was applied to, the checks performed, and known limitations.

## Out-of-Distribution and Domain-Shift Detection

This strategy covers how to detect inputs that fall outside the conditions under which a model was trained and validated. It supports the principle of uncertainty and reliability and addresses overfitting. It describes score-based detectors (softmax and energy scores), distance-based detectors (Mahalanobis and k-nearest-neighbour distance in embedding space), comparison of embeddings from application data with pretraining data, and temporal and metadata-based signals for time series, and it distinguishes methods that need access to embeddings from those that work with input and output access only. Detectors have to be calibrated on spatially blocked data and are used to complement uncertainty estimates, not to replace them. Minimum reporting: the detector and the signal it uses, the access it needs, detection performance on a held-out shift, and known limitations.

## Fairness and Bias Mitigation

This strategy covers how to measure and reduce geographic and other bias in data and models, and it supports the fairness principle. It describes auditing the coverage of training data across regions, climate zones, land cover types and sensors, reporting performance per region and group together with the gaps between them, reweighting, resampling and augmentation to balance data, representation-level and loss-level methods, and post-hoc adjustment, with guidance on when each suits pretraining, fine-tuning and downstream tasks. It also covers the choice of fairness metrics, which depends on the task and has to be justified. Minimum reporting: the groups or regions considered and why, the metrics, the gaps found, the mitigation applied, and known limitations.

## Privacy-Preserving Methods and Geoprivacy

This strategy covers how to protect personal data and sensitive locations in training, evaluation and release. It supports the privacy principle and addresses geoprivacy. It describes data minimisation and anonymisation, spatial aggregation, coarsening and masking of locations, differential privacy and other privacy-preserving training methods and their effect on accuracy, federated or access-controlled training where data cannot be shared, auditing of models for memorisation and membership inference, and review of outputs before release. Guidance covers how to choose among them by data type, resolution and use case. Minimum reporting: the data and locations considered sensitive, the measures applied, the privacy audit performed, the accuracy cost where measured, and known limitations.

## Adversarial Robustness and Security

This strategy covers how to test and improve resistance to deliberate manipulation. It supports the principle of robustness and security and addresses adversarial attacks. It describes threat modelling for EO pipelines, evasion testing with perturbed imagery, poisoning and backdoor checks on training and fine-tuning data, defences such as adversarial training, input validation and ensembles, protection of model artefacts and access, and monitoring for tampered or spoofed inputs. It separates black-box tests, which suit models held as background IP, from white-box tests. Minimum reporting: the threat model, the attacks and perturbation budgets tested, the results, the defences applied, and known limitations.

## Hallucination and Factual Reliability

This strategy covers how to limit and detect unsupported content in generative components and language-based agents, and it addresses hallucination. It describes grounding generated content in source data and knowledge graphs, consistency and cross-source checks, uncertainty and confidence flags on generated pixels or statements, labelling of generated content for users, and evaluation on benchmarks that test factual accuracy in EO tasks such as gap-filling, super-resolution and question answering. Minimum reporting: where generated content is produced, the checks used to detect unsupported content, the measured rate or error, how users are informed, and known limitations.

## Energy-Efficient and Green AI Methods

This strategy covers how to reduce and report the energy use and emissions of training and operation, and it supports the principle of energy efficiency. It describes measuring energy and emissions during training and inference, reducing cost through parameter-efficient fine-tuning, model compression and distillation, efficient data pipelines and mixed precision, reusing pretrained models, choosing efficient hardware and, where possible, renewable-powered HPC, and benchmarking the energy-to-solution ratio. Minimum reporting: hardware, runtime, estimated energy and emissions for training and for a reference inference workload, the efficiency measures applied, and known limitations.

## Human Oversight and Dual-Use Safeguards

This strategy covers how people stay in control of AI outputs and how misuse is limited. It supports the principle of social impact and addresses dual-use. It describes human-in-the-loop validation for high-stakes outputs, interfaces that show uncertainty and limitations to non-expert users, participatory design and stakeholder review, rules for who may access sensitive models and data, intended-use statements, and the review of sensitive use cases by an independent advisory or ethics body. Minimum reporting: the points where a person can review or override an output, the users and access conditions, the sensitive uses identified and how they were reviewed, and known limitations.
