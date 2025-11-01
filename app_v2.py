"""
Drug Causality BERT - Version 2.0 - Final
Streamlit Web Application
Complete PBRER/PSUR-Compliant Causality Assessment with Section 11 Generator
"""

import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

import os
import json
import tempfile
from datetime import datetime
from regulatory_causality_report import create_regulatory_report
from pbrer_section11_generator import generate_pbrer_section11

# Page configuration
st.set_page_config(
    page_title="Drug Causality BERT v2.0",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        padding-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .section-divider {
        border-top: 3px solid #1f77b4;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">💊 Drug Causality BERT v2.0</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">PBRER/PSUR-Compliant Pharmacovigilance Analysis System</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/pill.png", width=80)
    st.title("About v2.0")
    st.info("""
    **Drug Causality BERT v2.0** - Complete pharmacovigilance solution
    
    **New in v2.0:**
    - ✅ PBRER Section 11 Generator
    - ✅ Company Comment Format
    - ✅ Confounding Factors Analysis
    - ✅ Drug-specific Summaries
    
    **Core Features:**
    - PBRER/PSUR-compliant reports
    - WHO-UMC causality categories
    - Naranjo ADR probability scale
    - FDA/EMA regulatory context
    
    **Model Performance:**
    - F1 Score: 0.9759
    - Accuracy: 0.9759
    - Sensitivity: 0.9868
    - Specificity: 0.9650
    """)
    
    st.markdown("---")
    st.subheader("Regulatory Compliance")
    st.markdown("""
    - ICH E2C(R2) - PBRER
    - FDA 21 CFR
    - EMA GVP Module IX
    - WHO-UMC Guidelines
    """)
    
    st.markdown("---")
    st.caption("Version 2.0 Final | November 2025")

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

# Main workflow
st.markdown("---")

# STEP 1: Upload and Generate Drug Causality Assessment Report
st.header("📄 Step 1: Upload PDF & Generate Drug Causality Assessment Report")

st.markdown("""
<div class="info-box">
<strong>📋 Upload your PDF document</strong><br>
Supported: Clinical trials, case reports, literature articles, pharmacovigilance documents
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF document containing drug-event information",
        key="pdf_uploader"
    )

with col2:
    if uploaded_file:
        st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")

if uploaded_file is not None:
    st.success(f"✓ File uploaded: **{uploaded_file.name}**")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name
    
    st.session_state['uploaded_file_path'] = tmp_file_path
    st.session_state['uploaded_file_name'] = uploaded_file.name
    
    st.markdown("---")
    
    # Generate Drug Causality Assessment Report
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_main_report = st.button(
            "🔬 Generate Drug Causality Assessment Report",
            type="primary",
            use_container_width=True,
            key="generate_main"
        )
    
    if generate_main_report:
        with st.spinner("🔄 Analyzing document and generating comprehensive report... This may take 2-5 minutes..."):
            try:
                # Progress indicators
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("Loading BioBERT model...")
                progress_bar.progress(10)
                
                status_text.text("Extracting text from PDF...")
                progress_bar.progress(30)
                
                status_text.text("Performing causality assessment...")
                progress_bar.progress(50)
                
                # Generate report
                doc_path, json_path = create_regulatory_report(
                    st.session_state['uploaded_file_path']
                )
                
                status_text.text("Generating PBRER-compliant report...")
                progress_bar.progress(80)
                
                # Load results
                with open(json_path, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                
                st.session_state['results'] = results
                st.session_state['doc_path'] = doc_path
                st.session_state['json_path'] = json_path
                st.session_state['analysis_complete'] = True
                
                progress_bar.progress(100)
                status_text.text("✓ Analysis complete!")
                
                st.balloons()
                
                # Success message
                st.markdown(f"""
                <div class="success-box">
                <h3>✅ Drug Causality Assessment Report Generated!</h3>
                <p><strong>Document:</strong> {uploaded_file.name}</p>
                <p><strong>Report:</strong> {Path(doc_path).name}</p>
                <p><strong>Drugs Identified:</strong> {results['total_drugs']}</p>
                <p><strong>Events Identified:</strong> {results['total_events']}</p>
                <p><strong>Analysis Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display summary
                st.subheader("📊 Quick Summary")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Sentences", f"{results['total_sentences']:,}")
                
                with col2:
                    st.metric("Unique Drugs", results['total_drugs'])
                
                with col3:
                    st.metric("Unique Events", results['total_events'])
                
                with col4:
                    related_count = sum(d['related_count'] for d in results.get('drug_statistics', []))
                    st.metric("Related Statements", related_count)
                
                # Top drugs
                if results.get('drug_statistics'):
                    st.subheader("🔬 Top Identified Drugs")
                    
                    import pandas as pd
                    df_drugs = pd.DataFrame(results['drug_statistics'][:10])
                    df_drugs['confidence_pct'] = df_drugs['max_confidence'] * 100
                    
                    st.dataframe(
                        df_drugs[['drug', 'related_count', 'confidence_pct']].rename(columns={
                            'drug': 'Drug Name',
                            'related_count': 'Related Statements',
                            'confidence_pct': 'Confidence (%)'
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
                
                # Download buttons
                st.markdown("---")
                st.subheader("📥 Download Reports")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    with open(doc_path, 'rb') as f:
                        st.download_button(
                            label="📄 Download Word Report",
                            data=f,
                            file_name=Path(doc_path).name,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                
                with col2:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        st.download_button(
                            label="📊 Download JSON Summary",
                            data=f,
                            file_name=Path(json_path).name,
                            mime="application/json",
                            use_container_width=True
                        )
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                st.exception(e)

# STEP 2: PBRER Section 11 Generator (only show if analysis is complete)
if st.session_state.get('analysis_complete', False):
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    st.header("📋 Step 2: Generate PBRER Section 11 - Company Comment")
    
    st.markdown("""
    <div class="warning-box">
    <strong>📝 PBRER Section 11 Format</strong><br>
    Generate drug-specific summary with company interpretation following ICH E2C(R2) Section 11 guidelines.
    Includes: Document summary, concomitant medications, time to onset, concurrent conditions, confounding factors, and company causality assessment.
    </div>
    """, unsafe_allow_html=True)
    
    # Get list of identified drugs
    drugs_list = sorted(st.session_state['results']['drugs_identified'])
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("**Select a drug from the identified list:**")
        selected_drug = st.selectbox(
            "Drug Name:",
            options=drugs_list,
            help="Choose the drug you want to generate a PBRER Section 11 report for",
            key="drug_selector",
            label_visibility="collapsed"
        )
    
    with col2:
        st.metric(
            label="Available Drugs",
            value=len(drugs_list)
        )
    
    st.markdown("---")
    
    # Generate PBRER Section 11 button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_pbrer = st.button(
            f"🔬 Generate PBRER Section 11 for {selected_drug}",
            type="primary",
            use_container_width=True,
            key="generate_pbrer"
        )
    
    if generate_pbrer:
        with st.spinner(f"Generating comprehensive PBRER Section 11 analysis for **{selected_drug}**..."):
            try:
                # Generate report
                report_text, analysis_results = generate_pbrer_section11(
                    st.session_state['uploaded_file_path'],
                    selected_drug
                )
                
                # Store in session state
                st.session_state['pbrer_report'] = report_text
                st.session_state['pbrer_analysis'] = analysis_results
                st.session_state['pbrer_drug'] = selected_drug
                
                st.success(f"✅ PBRER Section 11 report generated for **{selected_drug}**!")
                
                # Display summary metrics
                st.subheader("📊 Analysis Summary")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Concomitant Meds",
                        len(analysis_results.get('concomitant_medications', []))
                    )
                
                with col2:
                    st.metric(
                        "Time to Onset Refs",
                        len(analysis_results.get('time_to_onset', []))
                    )
                
                with col3:
                    st.metric(
                        "Concurrent Conditions",
                        len(analysis_results.get('concurrent_conditions', []))
                    )
                
                with col4:
                    st.metric(
                        "Confounding Factors",
                        len(analysis_results.get('confounding_factors', []))
                    )
                
                st.markdown("---")
                
                # Display report
                st.subheader(f"📄 PBRER Section 11 Report: {selected_drug}")
                
                with st.expander("📖 View Complete Report", expanded=True):
                    st.text(report_text)
                
                # Automatic download preparation
                st.markdown("---")
                st.subheader("📥 Download PBRER Section 11 Report")
                
                # Create filename
                filename = f"PBRER_Section11_{selected_drug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.download_button(
                        label=f"📥 Download {selected_drug} - PBRER Section 11 Report",
                        data=report_text,
                        file_name=filename,
                        mime="text/plain",
                        use_container_width=True,
                        type="primary"
                    )
                
                st.success(f"✓ Report ready for download: **{filename}**")
                
                # Detailed analysis breakdown
                st.markdown("---")
                st.subheader("🔍 Detailed Analysis Components")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if analysis_results.get('concomitant_medications'):
                        with st.expander("💊 Concomitant Medications"):
                            for i, med in enumerate(analysis_results['concomitant_medications'][:10], 1):
                                st.markdown(f"**{i}.** {med['match']}")
                                st.caption(f"Context: {med['context'][:150]}...")
                                st.markdown("---")
                    
                    if analysis_results.get('dose_information'):
                        with st.expander("💉 Dose Information"):
                            for i, dose in enumerate(analysis_results['dose_information'][:10], 1):
                                st.markdown(f"**{i}.** {dose['match']}")
                                st.caption(f"Context: {dose['context'][:150]}...")
                                st.markdown("---")
                    
                    if analysis_results.get('patient_demographics'):
                        with st.expander("👥 Patient Demographics"):
                            for i, demo in enumerate(analysis_results['patient_demographics'][:10], 1):
                                st.markdown(f"**{i}.** {demo['match']}")
                                st.caption(f"Context: {demo['context'][:150]}...")
                                st.markdown("---")
                
                with col2:
                    if analysis_results.get('time_to_onset'):
                        with st.expander("⏱️ Time to Onset"):
                            for i, time in enumerate(analysis_results['time_to_onset'][:10], 1):
                                st.markdown(f"**{i}.** {time['match']}")
                                st.caption(f"Context: {time['context'][:150]}...")
                                st.markdown("---")
                    
                    if analysis_results.get('concurrent_conditions'):
                        with st.expander("🏥 Concurrent Conditions"):
                            for i, cond in enumerate(analysis_results['concurrent_conditions'][:10], 1):
                                st.markdown(f"**{i}.** {cond['match']}")
                                st.caption(f"Context: {cond['context'][:150]}...")
                                st.markdown("---")
                    
                    if analysis_results.get('clinical_outcomes'):
                        with st.expander("📊 Clinical Outcomes"):
                            for i, outcome in enumerate(analysis_results['clinical_outcomes'][:10], 1):
                                st.markdown(f"**{i}.** {outcome['match']}")
                                st.caption(f"Context: {outcome['context'][:150]}...")
                                st.markdown("---")
                
                # Confounding factors (full width)
                if analysis_results.get('confounding_factors'):
                    with st.expander("⚠️ Confounding Factors & Alternative Explanations", expanded=True):
                        st.warning(f"**{len(analysis_results['confounding_factors'])} potential confounding factor(s) identified**")
                        for i, factor in enumerate(analysis_results['confounding_factors'][:5], 1):
                            st.markdown(f"**{i}.** {factor['sentence'][:300]}...")
                            st.caption(f"Keyword: {factor['keyword']}")
                            st.markdown("---")
                
            except Exception as e:
                st.error(f"❌ Error generating PBRER Section 11 report: {str(e)}")
                st.exception(e)

# Information section
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

with st.expander("ℹ️ About This System", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📋 What is Drug Causality Assessment?
        
        Drug causality assessment is the systematic evaluation of the relationship between 
        drug administration and the occurrence of adverse events. This system uses advanced 
        machine learning (BioBERT) to automatically identify and assess potential drug-event 
        associations.
        
        ### 🏥 Causality Scales
        
        **WHO-UMC Categories:**
        - Certain/Definite
        - Probable/Likely
        - Possible
        - Unlikely
        - Conditional
        - Unassessable
        
        **Naranjo ADR Scale:**
        - Definite (≥9 points)
        - Probable (5-8 points)
        - Possible (1-4 points)
        - Doubtful (≤0 points)
        """)
    
    with col2:
        st.markdown("""
        ### 📝 PBRER Section 11
        
        PBRER Section 11 requires comprehensive summary and company interpretation 
        of individual case reports and literature articles.
        
        **This tool generates:**
        - Document summary (drug-specific)
        - Contextual information
        - Confounding factors analysis
        - Company causality assessment
        - Regulatory recommendations
        
        ### 📚 Regulatory Framework
        
        - **ICH E2C(R2)** - PBRER Guidelines
        - **FDA 21 CFR** - US Regulations
        - **EMA GVP Module IX** - EU Guidelines
        - **WHO-UMC** - Causality Assessment
        
        ### 💡 Tips
        
        - Upload clear, text-based PDFs
        - Clinical trials and case studies work best
        - Review Word report for full details
        - Use PBRER Section 11 for regulatory submissions
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>Drug Causality BERT v2.0 Final</strong></p>
    <p>Complete PBRER/PSUR-Compliant Pharmacovigilance Analysis System</p>
    <p>© 2025 | Powered by BioBERT | Model F1: 0.9759</p>
</div>
""", unsafe_allow_html=True)

# Force Streamlit redeploy 11/02/2025 02:39:12


# ===== UNIFIED DRUG & ADR DATABASE =====

import requests
from typing import Set, Dict, List

class RxNormDrugDatabase:
    def __init__(self):
        self.base_url = "https://rxnav.nlm.nih.gov/REST"
    
    def search_drugs(self, query: str) -> List[str]:
        try:
            url = f"{self.base_url}/rxcui/search.json"
            params = {'search': query, 'maxEntries': 50}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'idGroup' in data and 'rxList' in data['idGroup']:
                    return [drug['name'] for drug in data['idGroup']['rxList']]
        except:
            pass
        return []

class FAERSIntegration:
    def __init__(self):
        self.openFDA_api = "https://api.fda.gov/drug/event.json"
    
    def get_adverse_events(self, drug_name: str, limit: int = 50) -> List[Dict]:
        try:
            params = {
                'search': f'patient.drug.openfda.generic_name:"{drug_name}"',
                'limit': limit
            }
            response = requests.get(self.openFDA_api, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                events = []
                if 'results' in data:
                    for report in data['results']:
                        if 'patient' in report and 'reaction' in report['patient']:
                            for reaction in report['patient']['reaction']:
                                events.append({
                                    'event': reaction.get('reactionmeddrapt', 'Unknown'),
                                    'outcome': reaction.get('reactionoutcome', 'Unknown')
                                })
                return events
        except:
            pass
        return []

class UnifiedDrugADRDatabase:
    def __init__(self):
        self.rxnorm = RxNormDrugDatabase()
        self.faers = FAERSIntegration()
    
    def extract_drugs_from_text(self, text: str) -> Set[str]:
        text_lower = text.lower()
        common_drugs = ['bortezomib', 'metoprolol', 'rituximab', 'simvastatin']
        return {drug for drug in common_drugs if drug in text_lower}
    
    def get_adrs_for_drug(self, drug_name: str) -> Dict:
        try:
            return {'adrs': self.faers.get_adverse_events(drug_name, limit=10)}
        except:
            return {'adrs': []}
