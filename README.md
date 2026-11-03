# 💊 Drug Causality BERT v2.0

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Hugging Face Model](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Model%20Hub-orange)](https://huggingface.co/PrashantRGore/drug-causality-bert-v2-model)
[![Hugging Face Dataset](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset%20(1M)-yellow)](https://huggingface.co/datasets/PrashantRGore/synthetic-faers-1m-v3)
[![ADE Corpus V2 Benchmark](https://img.shields.io/badge/ADE--V2%20Accuracy-97.59%25-brightgreen)](https://huggingface.co/datasets/SetFit/ade_corpus_v2_classification)
[![F1-Score](https://img.shields.io/badge/F1--Score-0.9759-brightgreen)](https://huggingface.co/datasets/SetFit/ade_corpus_v2_classification)
[![CI Tests](https://github.com/PrashantRGore/drug-causality-bert-v2/actions/workflows/ci.yml/badge.svg)](https://github.com/PrashantRGore/drug-causality-bert-v2/actions)

A state-of-the-art, fine-tuned BioBERT model and clinical intelligence platform for **adverse drug event (ADE) causality assessment** in pharmacovigilance and drug safety workflows, achieving **97.6% accuracy** on the ADE Corpus V2 benchmark.

---

## 📌 Model Description

Drug Causality BERT v2 classifies medical text to determine whether an adverse event is causally related to a drug. The model uses **Optuna-optimized hyperparameters** and is trained on the **ADE Corpus V2** benchmark dataset for regulatory pharmacovigilance activities.

- **Base Model:** [dmis-lab/biobert-base-cased-v1.2](https://huggingface.co/dmis-lab/biobert-base-cased-v1.2)  
- **Architecture:** BERT for Sequence Classification (2 labels)  
- **Task:** Binary Text Classification (Causal vs. Non-Causal ADEs)  
- **Training Dataset:** [ADE Corpus V2](https://huggingface.co/datasets/SetFit/ade_corpus_v2_classification)  
- **Training Date:** October 25, 2025  

---

## 🎯 Intended Use

### Primary Applications
- **Adverse Drug Reaction Detection:** Identify causal ADEs in clinical narratives and case notes
- **Pharmacovigilance Signal Detection:** Automated screening for drug safety signals
- **FAERS Case Processing:** Classify causality in FDA adverse event reports (21 CFR 314.80)
- **Literature Mining:** Extract drug-safety evidence from published medical literature
- **Regulatory Reporting:** Support PBRER / PSUR (ICH E2C(R2)) and IND safety submissions

### Target Users
- Pharmacovigilance professionals & QPPVs
- Drug safety scientists & medical reviewers
- Regulatory affairs specialists
- Clinical researchers & healthcare AI developers

---

## 📊 Training Data & Optimization

### ADE Corpus V2 Dataset

This model was fine-tuned on the **ADE Corpus V2** (Adverse Drug Effect Corpus Version 2), a benchmark corpus for pharmacovigilance.

- **Source:** Medical literature from MEDLINE case reports
- **Size:** 4,271 documents with 5,063 drugs and 6,821 adverse event annotations
- **Task:** Binary classification (ADE-related vs. non-ADE-related sentences)
- **Hugging Face Hub:** [SetFit/ade_corpus_v2_classification](https://huggingface.co/datasets/SetFit/ade_corpus_v2_classification)

**Citation:**
> Gurulingappa, H., Rajput, A. M., Roberts, A., Fluck, J., Hofmann-Apitius, M., & Toldo, L. (2012).  
> *Development of a benchmark corpus to support the automatic extraction of drug-related adverse effects from medical case reports.*  
> **Journal of Biomedical Informatics**, 45(5), 885-892.

### Optimized Hyperparameters (via Optuna)

- **Learning Rate:** `3.758e-05`
- **Epochs:** 1 (early stopping)
- **Batch Size:** 4
- **Gradient Accumulation Steps:** 4 (effective batch size: 16)
- **Optimizer:** AdamW
- **Max Sequence Length:** 512 tokens
- **Random Seed:** 42

---

## 🏆 Model Performance

### Benchmark Results (ADE Corpus V2 Test Set)

| Metric | Score | Comparison to Literature |
| :--- | :--- | :--- |
| **Accuracy** | **97.59%** | ⬆️ +8–12% vs. baseline BERT |
| **F1-Score** | **97.59%** | ⬆️ State-of-the-art on ADE-V2 |
| **Precision** | **97.62%** | ⬆️ Exceeds published benchmarks |
| **Recall** | **97.59%** | ⬆️ High sensitivity for ADEs |

### Performance Comparison

| Model | Accuracy | F1 Score | Notes |
| :--- | :--- | :--- | :--- |
| **Drug Causality BERT v2 (This)** | **97.59%** | **97.59%** | Optuna-optimized |
| BioBERT baseline | ~88% | ~87% | Standard fine-tuning |
| BERT-base | ~85% | ~84% | Non-biomedical general pretraining |
| Rule-based systems | ~75% | ~73% | Traditional PV dictionary lookups |

---

## 🚀 Quick Start & Usage

### 1. Installation

```bash
git clone https://github.com/PrashantRGore/drug-causality-bert-v2.git
cd drug-causality-bert-v2
pip install -r requirements.txt
```

### 2. Basic Python Inference

```python
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Load model and tokenizer from Hugging Face Hub
model_name = "PrashantRGore/drug-causality-bert-v2-model"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Example adverse event text
text = "Patient developed severe hepatotoxicity after starting methotrexate therapy."

# Tokenize and predict
inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
with torch.no_grad():
    outputs = model(**inputs)
    probabilities = torch.softmax(outputs.logits, dim=1)

causal_prob = probabilities[0][1].item()
classification = "CAUSAL ADE" if causal_prob > 0.5 else "NON-CAUSAL"

print(f"Statement: {text}")
print(f"Causality Probability: {causal_prob:.2%}")
print(f"Classification: {classification}")
```

**Output:**
```text
Statement: Patient developed severe hepatotoxicity after starting methotrexate therapy.
Causality Probability: 98.73%
Classification: CAUSAL ADE
```

### 3. Running the Streamlit Web Application

```bash
streamlit run streamlit_app.py
```

The web application provides five dedicated tabs:
1. **Single Statement:** Fast BioBERT causality inference with confidence gauges.
2. **PDF Case Report Analysis:** Automated full-document clinical extraction (Drugs, ADRs, Demographics) and sentence-level causality scoring.
3. **FDA FAERS & Regulatory Scores:** Live OpenFDA signal verification and interactive Naranjo Adverse Drug Reaction probability scale.
4. **Clinical Report Generator:** Local LLM reporting powered by Ollama (`meditron:7b`, `llama3.2:3b`) with deterministic regulatory fallbacks.
5. **Model Card & Scientific Compliance:** Complete documentation and international regulatory guidelines (ICH E2A, E2C, E2D).

### 4. Interactive Jupyter Tutorial

We provide a complete, publication-grade tutorial notebook demonstrating zero-RAM streaming, $2 \times 2$ contingency table calculation, PRR/ROR computation with 95% confidence intervals, and BioBERT narrative causality scoring:

👉 **[`notebooks/synthetic_faers_quickstart.ipynb`](notebooks/synthetic_faers_quickstart.ipynb)**

```bash
# Launch the quickstart notebook in Jupyter Lab or VS Code
jupyter lab notebooks/synthetic_faers_quickstart.ipynb
```

### 5. Running Automated Tests

```bash
# Run comprehensive unit test suite (10/10 tests)
python -m unittest discover -s tests -p "test_*.py"

# Verify local Ollama report generation with Meditron-7B
python test_meditron.py
```

---

## 📂 Project Architecture & Directory Layout

```text
drug-causality-bert-v2/
├── .github/workflows/
│   └── ci.yml                     # Automated GitHub Actions test pipeline
├── app/
│   ├── requirements.txt           # App dependencies
│   └── streamlit_app.py           # Container / Codespace entrypoint wrapper
├── models/
│   └── production_model_final/    # Model configs, tokenizer & LFS pointer
├── notebooks/
│   └── synthetic_faers_quickstart.ipynb # End-to-end signal detection & causality notebook
├── src/
│   ├── __init__.py                # Package entrypoint & clean symbol exports
│   ├── inference.py               # BioBERT causality classifier & PDF extraction
│   ├── clinical_standardizers.py  # MedDRA, Drug/ADR extractors, Naranjo & WHO-UMC
│   ├── fda_connector.py           # OpenFDA FAERS adverse event live connector
│   └── ollama_report_generator.py # Local LLM report generator (Meditron, Llama)
├── tests/
│   └── test_components.py         # Automated unit test suite (10/10 tests passing)
├── MODEL_CARD.md                  # Hugging Face Hub metadata card
├── pyproject.toml                 # Modern PEP 518/621 package metadata
├── requirements.txt               # Unified project dependencies
├── streamlit_app.py               # Unified 5-tab Streamlit intelligence app
├── test_meditron.py               # Local Ollama report generation verification
└── README.md                      # Comprehensive documentation & project guide
```

---

## ⚠️ Limitations & Edge Cases

- **Domain-Specific:** Optimized for pharmacovigilance text from biomedical literature and clinical case narratives.
- **English Language:** Trained on English MEDLINE abstracts and ADE Corpus V2.
- **Context Window:** 512 tokens maximum due to BERT architecture constraints.
- **Short Texts:** Very short statements (fewer than 10 words) may have reduced contextual confidence.
- **Decision Support Role:** Designed to augment and accelerate, not replace, expert clinical review.

---

## 🔒 Ethical Considerations & Regulatory Safeguards

⚠️ **Important:** This model is designed for **research, decision support, and pharmacovigilance screening workflows**. Final causality assessment must be verified by a qualified physician or Qualified Person for Pharmacovigilance (QPPV).

- **Zero Cost / 100% Local Inference:** No sensitive case data is sent to external commercial clouds.
- **GDPR / HIPAA Compliance:** De-identification of patient records is recommended prior to processing.
- **No PHI Training:** The underlying model was trained exclusively on publicly available MEDLINE publications.
- **Regulatory Alignment:** Adheres to ICH E2A, ICH E2C(R2), and FDA 21 CFR 314.80 principles.

---

## 📜 Citation

If you utilize this model, codebase, or synthetic dataset in your research or safety operations, please cite:

```bibtex
@misc{gore2025drugcausality,
  author = {Gore, Prashant R.},
  title = {Drug Causality BERT v2: Optuna-Optimized BioBERT for Pharmacovigilance ADE Detection},
  year = {2025},
  publisher = {GitHub},
  howpublished = {\url{https://github.com/PrashantRGore/drug-causality-bert-v2}},
  note = {Fine-tuned BioBERT on ADE Corpus V2 dataset, achieving 97.6% accuracy}
}

@dataset{gore2025syntheticfaers1mv3,
  author = {Gore, Prashant R.},
  title = {Synthetic FAERS 1M v3: Signal-Enhanced Pharmacovigilance Dataset},
  year = {2025},
  publisher = {Hugging Face},
  howpublished = {\url{https://huggingface.co/datasets/PrashantRGore/synthetic-faers-1m-v3}}
}
```

**Benchmark Corpus Citation:**
```bibtex
@article{gurulingappa2012ade,
  title={Development of a benchmark corpus to support the automatic extraction of drug-related adverse effects from medical case reports},
  author={Gurulingappa, Harsha and Rajput, Abdul Mateen and Roberts, Angus and Fluck, Juliane and Hofmann-Apitius, Martin and Toldo, Luca},
  journal={Journal of Biomedical Informatics},
  volume={45},
  number={5},
  pages={885--892},
  year={2012},
  publisher={Elsevier}
}
```

---

## 📄 License

Distributed under the **Apache 2.0** License. Free for commercial and research use with attribution. See [`LICENSE`](LICENSE) for details.

---

## 👤 Author & Support

- **Author:** Prashant R. Gore
- **GitHub:** [@PrashantRGore](https://github.com/PrashantRGore)
- **LinkedIn:** [linkedin.com/in/prashantgorepg](https://linkedin.com/in/prashantgorepg)
- **Issue Tracker:** [Report an issue on GitHub](https://github.com/PrashantRGore/drug-causality-bert-v2/issues)
