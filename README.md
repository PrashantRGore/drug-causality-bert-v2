# 💊 Drug Causality BERT V2.0

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

- Automated PDF Analysis: Upload medical literature and get instant causality assessments  
- Drug/ADR Extraction: Automatic extraction with dropdown selection for refinement  
- Multi-Algorithm Assessment: WHO-UMC, Naranjo Scale, and Karch & Lasagna algorithms

### Regulatory Compliance

- MedDRA Standardization: Automatic mapping to MedDRA preferred terms  
- FDA FAERS Integration: Real-world adverse event data lookup  
- PBRER Section 11 Reports: Auto-generated reports compliant with regulatory standards

### Advanced Capabilities

- Batch Processing: Analyze multiple documents simultaneously  
- Medical Text Preprocessing: Enhanced NLP with domain-specific cleaning  
- Causality Scoring: Multi-dimensional assessment (certain/probable/possible/unlikely)  
- Ollama LLM Integration: Local multi-model support (llama3.2, meditron, mistral) for professional report generation without any cloud API

## 🛠️ Installation and Setup

### Prerequisites

- Python 3.11  
- Git  
- Ollama AI Platform (https://ollama.com/download)

### Local Model Download

After installing Ollama, pull the required models locally:

ollama pull llama3.2:3b
ollama pull meditron:7b
ollama pull mistral:7b


### How It Works

- This project uses **Ollama local LLMs** for clinical and PBRER report generation to ensure complete privacy and no cloud API calls.  
- Models **are NOT stored in this repo**, nor managed with Git LFS. Ollama handles model downloads and caching locally.  
- Before running the app, make sure Ollama is installed and models pulled as shown above.  

### Running the Application
streamlit run streamlit_app.py

## 🤗 Model

BioBERT-based causality classification model:

- **Repository**: PrashantRGore/drug-causality-bert-v2-model  
- **Trained on**: ADE Corpus V2 dataset (CSIRO)

## 🙏 Acknowledgments

- **ADE Corpus V2** by CSIRO: Benchmark dataset for drug-adverse event detection  
  Gurulingappa, Harsha, et al. "Development of a benchmark corpus to support the automatic extraction of drug-related adverse effects from medical case reports." *Journal of Biomedical Informatics*, 45(5), 885-892, 2012.

- **BioBERT Team**: Pretrained biomedical language model used for fine tuning  
  Lee, Jinhyuk, et al. "BioBERT: a pre-trained biomedical language representation model for biomedical text mining." *Bioinformatics*, 36(4), 1234-1240, 2020.

- **Streamlit**: For the interactive web framework

- **Hugging Face**: For hosting pretrained models and providing transformers library

- **FDA**: For publicly available FAERS adverse event datasets

- **WHO-UMC**: For causality assessment scales

- **Naranjo et al.**: For the adverse drug reaction probability scales

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.


## 🐛 Issues

Report bugs [here](https://github.com/PrashantRGore/drug-causality-bert-v2/issues).

---

**Note:** All Ollama LLM models must be pulled locally for the report generation features to function. There are no large model files stored in this repo. The Hugging Face BioBERT model is pulled automatically via transformers.

Clinical decisions should always be made by qualified healthcare professionals.

---
