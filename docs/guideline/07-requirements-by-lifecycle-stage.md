# Requirements by Lifecycle Stage

This section turns the principles and risks into requirements that a developer can follow in the order of their own work. It is organised by lifecycle stage (data collection and curation, model design and training, evaluation and validation, release and documentation, and deployment and monitoring), which matches the stages of the compliance card. In each subsection a table lists the requirements for that stage, each with an identifier, a binding level (must, should or may), the principle or risk it addresses, the role responsible and the evidence to submit. Requirements marked must apply from this version. Requirements that depend on tools still being developed are marked should and become mandatory in version 2. Requirements are written so that they can be checked with input and output evidence, which allows them to apply to proprietary or third-party models.

## Data Collection and Curation

This subsection covers what is done before data are used for training or evaluation. It includes recording the provenance, licence and intended use of each dataset, screening for personal data and for sensitive locations (geoprivacy), documenting spatial, temporal, sensor and land cover coverage so that gaps and bias can be seen, designing training, calibration and test splits that are spatially blocked to avoid leakage, and recording the data in the machine-readable metadata. Each requirement is linked to the principles on privacy, fairness and transparency and to the risks of overfitting and geoprivacy, and is coordinated with the data management plan.

## Model Design and Training

This subsection covers requirements that apply while a model is designed, pretrained or fine-tuned. It includes recording the model's intended use, architecture, data sources and training configuration, logging compute and energy use, choosing and documenting an uncertainty approach, applying privacy-preserving and security measures in the training pipeline where the data or the use case call for them, protecting the pipeline and model artefacts from tampering, and keeping the work reproducible. Each requirement is linked to the principles on uncertainty, privacy, robustness and security, and energy efficiency, and to the strategies that describe the methods.

## Evaluation and Validation

This subsection covers the evidence a developer produces before a model is released. It includes validation on spatially blocked data and on regions, seasons and sensors not seen in training, calibration and coverage results for the stated uncertainty, performance reported per region or group so that gaps are visible, out-of-distribution and domain-shift tests, robustness tests against natural perturbations and adversarial inputs, privacy checks such as membership inference where relevant, and checks that explanations are faithful to the model. Requirements specify the minimum reporting for each test and distinguish tests that can be run with input and output access only from those that need access to model internals.

## Release and Documentation

This subsection covers what is submitted when a model, dataset or service is released. It includes the completed compliance card with a justification and evidence for each parameter, the machine-readable responsible AI metadata, a statement of intended use, known limitations and conditions of validity, the uncertainty and performance reports, and the sign-off by the responsible party. It also describes the release gate in practice: who reviews the submission, how long the review takes, and what has to be resubmitted when a requirement is not met. Who may approve, defer or block a release, and how exceptions are requested and recorded, are defined in the governance section.

## Deployment and Monitoring

This subsection covers requirements for models and services once they are in use, including in operational and demonstration settings. It includes monitoring for drift and out-of-distribution inputs, communicating uncertainty and generated content to users, human oversight and the ability to override or reject outputs, reporting and handling incidents such as harmful outputs or security events, and the management of updates, including re-validation when a model is retrained or replaced. It links to the principles on social impact, robustness and transparency and to the governance and monitoring section.
