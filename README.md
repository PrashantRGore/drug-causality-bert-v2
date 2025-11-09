# 💊 Drug Causality BERT V2.0

Advanced BioBERT-based system for automated drug-adverse event causality assessment with regulatory report generation capabilities.

## 🚀 Live Demo

**Try the App**

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


## 🤗 Model

BioBERT-based causality classification model:

- **Repository**: PrashantRGore/drug-causality-bert-v2-model  
- **Trained on**: ADE Corpus V2 dataset (CSIRO)

## 📄 License

Apache License 2.0

## 🤝 Contributing

Contributions welcome! Please submit a pull request.

## 🐛 Issues

Report bugs [here](https://github.com/PrashantRGore/drug-causality-bert-v2/issues).

**Note**: Ollama LLM models must be pulled locally for report generation feature to work.


