# 🇪🇺 EU AI Act Transparency Auditor

A professional compliance scanner tailored specifically for the German industrial market, designed to audit technical documents against the **May 8, 2026 Draft Guidelines** from the European Commission regarding Article 50 (Transparency & Disclosure).

##  Overview

This application provides a highly polished Streamlit UI to upload AI system technical documents (PDFs) and instantly generates a **Compliance Readiness Score**. The analysis is powered by a Haystack 2.0 pipeline integrating Google's Gemini API, but built with **Sovereign AI** principles in mind to ensure local data privacy and strict compliance with European data sovereignty standards. 

The core features include:
- **AI-User Disclosure Detection**: Analyzes whether users are clearly informed they are interacting with an AI system.
- **Deepfake & Synthetic Content Labeling**: Checks for appropriate labeling of artificially generated content.
- **Watermarking Standards**: Audits the presence of machine-readable watermarking conforming to the latest EU regulations.
- **Bilingual Support**: Seamless German/English UI toggle for local and international stakeholders.

##  Technology Stack
- **Frontend**: [Streamlit](https://streamlit.io/) (High-end UI, Bilingual Toggle)
- **Backend / LLM Orchestration**: [Haystack 2.0](https://haystack.deepset.ai/) (Pipeline routing, PDF Extraction, Prompt Building)
- **Model**: Google Gemini 1.5 Pro via `google-ai-haystack`
- **Security / Privacy**: Architecture designed to align with Sovereign AI practices, processing documents strictly in-memory and avoiding unauthorized third-party logging.

##  Installation & Usage

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/ai-compliance-pro.git
   cd ai-compliance-pro
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**
   Create a `.env` file in the root directory and add your Google API key:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

4. **Run the Application**
   ```bash
   streamlit run app.py
   ```

## 🔒 Commitment to Sovereign AI

In the context of the European industrial market, data privacy is paramount. This project is a demonstration of **Sovereign AI** principles: ensuring that sensitive technical documentation is processed securely, analyzed locally (where possible), and that enterprise compliance data remains strictly confidential without vendor lock-in or unauthorized model training.

---
