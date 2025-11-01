# GitHub Deployment Guide - Drug Causality BERT v2.0

## 📦 Preparing for GitHub Deployment

### Step 1: Initialize Git Repository

```bash
cd c:\Users\koreo\drug-causality-bert

# Initialize git (if not already done)
git init

# Copy the new .gitignore
copy .gitignore_v2 .gitignore
```

### Step 2: Create GitHub Repository

1. Go to [GitHub](https://github.com)
2. Click "New Repository"
3. Repository name: `drug-causality-bert-v2`
4. Description: "PBRER/PSUR-Compliant Drug-Event Causality Assessment System v2.0"
5. Choose Public or Private
6. **Do NOT** initialize with README (we have our own)
7. Click "Create repository"

### Step 3: Prepare Files for Commit

```bash
# Stage all files
git add .

# Create initial commit
git commit -m "Initial commit: Drug Causality BERT v2.0 with PBRER/PSUR compliance and Streamlit app"

# Add remote repository (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/drug-causality-bert-v2.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## 🚀 Deploying Streamlit App

### Option 1: Streamlit Community Cloud (Recommended)

#### Prerequisites
- GitHub repository is public
- Files are pushed to GitHub

#### Deployment Steps

1. **Go to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub

2. **Deploy New App**
   - Click "New app"
   - Select your repository: `drug-causality-bert-v2`
   - Branch: `main`
   - Main file path: `app.py`
   - Click "Deploy!"

3. **Wait for Deployment**
   - Streamlit will install dependencies from `requirements_v2.txt`
   - This may take 5-10 minutes
   - Your app will be available at: `https://YOUR_USERNAME-drug-causality-bert-v2.streamlit.app`

#### Configuration

Create `.streamlit/config.toml` (optional):

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 200
enableXsrfProtection = true
```

### Option 2: Heroku Deployment

#### Prerequisites
- Heroku account
- Heroku CLI installed

#### Files Needed

Create `Procfile`:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

Create `setup.sh`:
```bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

#### Deployment Commands

```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create drug-causality-bert-v2

# Push to Heroku
git push heroku main

# Open app
heroku open
```

### Option 3: Docker Deployment

#### Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements_v2.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_v2.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"

# Copy application files
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Build and Run

```bash
# Build Docker image
docker build -t drug-causality-bert-v2 .

# Run container
docker run -p 8501:8501 drug-causality-bert-v2

# Access at http://localhost:8501
```

#### Push to Docker Hub

```bash
# Tag image
docker tag drug-causality-bert-v2 YOUR_DOCKERHUB_USERNAME/drug-causality-bert-v2:latest

# Push to Docker Hub
docker push YOUR_DOCKERHUB_USERNAME/drug-causality-bert-v2:latest
```

## 📝 Important Notes

### Model Files

The BioBERT model files are large (437 MB). You have two options:

#### Option 1: Git LFS (Large File Storage)

```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "models/production_model_final/model.safetensors"
git lfs track "models/production_model_final/pytorch_model.bin"

# Add .gitattributes
git add .gitattributes

# Commit and push
git add models/
git commit -m "Add model files with Git LFS"
git push
```

#### Option 2: External Download (Recommended)

Add to README:

```markdown
## Model Download

The BioBERT model is not included in the repository due to size.

Download from:
- [Hugging Face](https://huggingface.co/your-model-link)
- [Google Drive](https://drive.google.com/your-link)

Place files in: `models/production_model_final/`
```

### Environment Variables

For sensitive information, use environment variables:

Create `.streamlit/secrets.toml` (NOT committed to Git):

```toml
# API keys or sensitive data
API_KEY = "your-api-key"
```

Access in code:

```python
import streamlit as st
api_key = st.secrets["API_KEY"]
```

## 🔒 Security Best Practices

1. **Never commit sensitive data**
   - API keys
   - Passwords
   - Personal information

2. **Use .gitignore**
   - Exclude large files
   - Exclude generated reports
   - Exclude temporary files

3. **Environment variables**
   - Use Streamlit secrets
   - Use Heroku config vars
   - Use Docker environment variables

## 📊 Repository Structure for GitHub

```
drug-causality-bert-v2/
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions (optional)
│
├── .streamlit/
│   └── config.toml                   # Streamlit configuration
│
├── src/
│   ├── __init__.py
│   └── inference.py
│
├── models/
│   └── production_model_final/
│       ├── config.json
│       ├── tokenizer.json
│       ├── vocab.txt
│       └── README.md                 # Model download instructions
│
├── data/
│   └── raw/
│       └── .gitkeep                  # Keep empty folder
│
├── results/
│   └── .gitkeep
│
├── app.py                            # Streamlit app ⭐
├── regulatory_causality_report.py    # Main script
├── pbrer_psur_templates.py          # Language templates
├── drug_causality_regulatory.ipynb  # Jupyter notebook
│
├── requirements_v2.txt               # Dependencies ⭐
├── README_v2.md                      # Main README ⭐
├── LICENSE                           # License file
├── .gitignore                        # Git ignore
├── Procfile                          # Heroku (if using)
├── Dockerfile                        # Docker (if using)
│
└── docs/
    ├── GITHUB_DEPLOYMENT_GUIDE.md    # This file
    ├── COMPLETE_IMPLEMENTATION_SUMMARY.md
    ├── REGULATORY_REPORT_GUIDE.md
    └── VERIFICATION_SUMMARY.md
```

## 🎯 Post-Deployment Checklist

- [ ] Repository created on GitHub
- [ ] All files committed and pushed
- [ ] .gitignore properly configured
- [ ] README_v2.md is the main README
- [ ] Model files handled (LFS or external download)
- [ ] Streamlit app deployed
- [ ] App URL tested and working
- [ ] Documentation updated with app URL
- [ ] License file added
- [ ] Repository description updated
- [ ] Topics/tags added to repository

## 🌐 Sharing Your App

Once deployed, share your app:

1. **Update README** with app URL:
   ```markdown
   ## 🚀 Live Demo
   
   Try the app: [Drug Causality BERT v2.0](https://your-app-url.streamlit.app)
   ```

2. **Add badge to README**:
   ```markdown
   [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)
   ```

3. **Social media**:
   - LinkedIn
   - Twitter
   - Reddit (r/MachineLearning, r/bioinformatics)

## 🐛 Troubleshooting

### Streamlit Cloud Issues

**Problem**: App won't start  
**Solution**: Check `requirements_v2.txt` for correct versions

**Problem**: Model not found  
**Solution**: Ensure model files are in correct directory or add download script

**Problem**: Memory limit exceeded  
**Solution**: Optimize model loading, use caching

### Heroku Issues

**Problem**: Slug size too large  
**Solution**: Use .slugignore to exclude unnecessary files

**Problem**: Timeout during build  
**Solution**: Reduce dependencies, use lighter base image

### Docker Issues

**Problem**: Image too large  
**Solution**: Use multi-stage builds, alpine base image

**Problem**: Port not accessible  
**Solution**: Ensure EXPOSE 8501 and correct port mapping

## 📞 Support

If you encounter issues:

1. Check [Streamlit Community Forum](https://discuss.streamlit.io)
2. Review [GitHub Issues](https://github.com/YOUR_USERNAME/drug-causality-bert-v2/issues)
3. Consult deployment platform documentation

## ✅ Final Steps

```bash
# Tag version 2.0
git tag -a v2.0 -m "Version 2.0: PBRER/PSUR compliance and Streamlit app"
git push origin v2.0

# Create release on GitHub
# Go to: https://github.com/YOUR_USERNAME/drug-causality-bert-v2/releases
# Click "Create a new release"
# Select tag: v2.0
# Add release notes
# Publish release
```

---

**Congratulations! Your Drug Causality BERT v2.0 is now deployed! 🎉**
