---
language: en
license: apache-2.0
tags:
- pharmacovigilance
- drug-safety
- adverse-drug-reactions
- clinical-nlp
- biobert
- text-classification
- drug-causality
- ade-corpus
- medical-nlp
datasets:
- SetFit/ade_corpus_v2_classification
library_name: transformers
pipeline_tag: text-classification
base_model: dmis-lab/biobert-base-cased-v1.2
widget:
- text: "Patient developed severe rash after taking amoxicillin"
  example_title: "Causal ADE"
- text: "Blood pressure normalized with lisinopril treatment"
  example_title: "Non-causal"
- text: "Hepatotoxicity observed following methotrexate administration"
  example_title: "Causal ADE"
---

# Drug Causality BERT v2 Model Card

A fine-tuned BioBERT model for **adverse drug event (ADE) causality assessment** in pharmacovigilance workflows, achieving **97.6% accuracy** on the ADE Corpus V2 benchmark.

## Model Description

Drug Causality BERT v2 classifies medical text to determine whether an adverse event is causally related to a drug. The model uses **Optuna-optimized hyperparameters** and is trained on the **ADE Corpus V2** dataset for regulatory pharmacovigilance activities.

- **Base Model:** [dmis-lab/biobert-base-cased-v1.2](https://huggingface.co/dmis-lab/biobert-base-cased-v1.2)
- **Architecture:** BERT for Sequence Classification (2 labels)
- **Task:** Binary Text Classification (Causal vs Non-Causal ADEs)
- **Training Dataset:** [ADE Corpus V2](https://huggingface.co/datasets/SetFit/ade_corpus_v2_classification)
- **GitHub Repository:** [PrashantRGore/drug-causality-bert-v2](https://github.com/PrashantRGore/drug-causality-bert-v2)
- **Accuracy:** 97.59% | **F1 Score:** 0.9759
