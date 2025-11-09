# 💊 Drug Causality BERT V2.0

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://drug-causality-bert-v2-tweghknxn5ve46tymrq27g.streamlit.app/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

Advanced BioBERT-based system for automated drug-adverse event causality assessment with regulatory report generation capabilities.

## 🚀 Live Demo

**[Try the App](https://drug-causality-bert-v2-tweghknxn5ve46tymrq27g.streamlit.app/)**

## 📊 Performance Metrics

- **F1 Score**: 97.59%
- **Accuracy**: 97.59%
- **Sensitivity**: 98.68%
- **Specificity**: 96.50%

## ✨ Key Features

### Core Functionality
- **Automated PDF Analysis**: Upload medical literature and get instant causality assessments
- **Drug/ADR Extraction**: Automatic extraction with dropdown selection for refinement
- **Multi-Algorithm Assessment**: WHO-UMC, Naranjo Scale, and Karch & Lasagna algorithms

### Regulatory Compliance
- **MedDRA Standardization**: Automatic mapping to MedDRA preferred terms
- **FDA FAERS Integration**: Real-world adverse event data lookup
- **PBRER Section 11 Reports**: Auto-generated reports compliant with regulatory standards

### Advanced Capabilities
- **Batch Processing**: Analyze multiple documents simultaneously
- **Medical Text Preprocessing**: Enhanced NLP with domain-specific cleaning
- **Causality Scoring**: Multi-dimensional assessment (certain/probable/possible/unlikely)

## 🛠️ Installation

### Prerequisites
- Python 3.11
- Git

### Local Setup


## 🤗 Model

The BioBERT model is hosted on Hugging Face Hub:
- **Repository**: [PrashantRGore/drug-causality-bert-v2-model](https://huggingface.co/PrashantRGore/drug-causality-bert-v2-model)
- **Base Model**: BioBERT
- **Size**: 438 MB
- **Fine-tuned on**: ADE Corpus V2 dataset

## 📊 Dataset

This model was trained on the **ADE Corpus V2** dataset:

**ADE Corpus V2** (Adverse Drug Event Corpus)
- **Source**: CSIRO (Commonwealth Scientific and Industrial Research Organisation)
- **Content**: Medical case reports annotated for drug-adverse event relationships
- **Size**: 23,516 sentences from PubMed abstracts
- **Annotations**: Binary classification (related/not related)
- **Citation**: Gurulingappa et al. (2012)

### Dataset Reference


## 💻 Usage

### Single Statement Classification


### PDF Analysis

Upload a PDF through the Streamlit interface for:
- Automatic drug and adverse event extraction
- Sentence-by-sentence causality assessment
- FDA FAERS database lookup
- Regulatory report generation

### Regulatory Report Generation

The app automatically generates:
1. **Drug Causality Event Report**: Detailed assessment with temporal relationship and mechanism analysis
2. **PBRER Section 11 Summary**: Regulatory-compliant summary tables

## 📦 Dependencies

Key packages:
- `streamlit>=1.28.0`
- `torch>=2.5.0`
- `transformers>=4.35.0`
- `PyPDF2>=3.0.1`
- `nltk>=3.7`
- `pandas`, `numpy`, `scikit-learn`
- `python-docx`, `requests`

## 🔧 Configuration

### Threshold Settings
- **0.3-0.4**: High sensitivity (catch all events)
- **0.5**: Balanced performance (default)
- **0.7-0.8**: High precision (reduce false alarms)

### Causality Algorithms

**WHO-UMC Scale**:
- Certain/Probable/Possible/Unlikely/Conditional/Unassessable

**Naranjo Scale**:
- Definite (≥9) / Probable (5-8) / Possible (1-4) / Doubtful (≤0)

**Karch & Lasagna**:
- Definite/Probable/Possible/Conditional

## 🚀 Deployment

### Streamlit Cloud
1. Fork this repository
2. Connect to Streamlit Cloud
3. Set main file: `streamlit_app.py`
4. Deploy

### Local Development

## 📝 Citation

If you use this project in your research, please cite:

@software{drug_causality_bert_v2,
author = {Gore, Prashant R.},
title = {Drug Causality BERT V2.0: Advanced Causality Assessment System},
year = {2025},
url = {https://github.com/PrashantRGore/drug-causality-bert-v2}
}


## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🐛 Issues

Found a bug? Please open an issue [here](https://github.com/PrashantRGore/drug-causality-bert-v2/issues).

## 👨‍💻 Author

**Prashant R. Gore**
- GitHub: [@PrashantRGore](https://github.com/PrashantRGore)
- Model: [Hugging Face](https://huggingface.co/PrashantRGore/drug-causality-bert-v2-model)

## 🙏 Acknowledgments

- **ADE Corpus V2**: CSIRO for providing the benchmark dataset for drug-adverse event extraction
- **BioBERT team**: For the pre-trained biomedical language model (Lee et al., 2020)
- **Streamlit**: For the excellent web framework
- **Hugging Face**: For model hosting infrastructure and transformers library
- **FDA**: For public access to FAERS adverse event database
- **WHO-UMC**: For the causality assessment scale
- **Naranjo et al.**: For the adverse drug reaction probability scale

### Key References

1. **Gurulingappa, H., et al. (2012)**. "Development of a benchmark corpus to support the automatic extraction of drug-related adverse effects from medical case reports." *Journal of Biomedical Informatics*, 45(5), 885-892.

2. **Lee, J., et al. (2020)**. "BioBERT: a pre-trained biomedical language representation model for biomedical text mining." *Bioinformatics*, 36(4), 1234-1240.

3. **Naranjo, C.A., et al. (1981)**. "A method for estimating the probability of adverse drug reactions." *Clinical Pharmacology & Therapeutics*, 30(2), 239-245.

---

**Note**: This is a research tool. Clinical decisions should always be made by qualified healthcare professionals.