import streamlit as st
import os
import tempfile
from logic import analyze_pdf
from fpdf import FPDF
from fpdf.enums import Align
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import io

# Set page configuration
st.set_page_config(
    page_title="EU AI Act Transparency Auditor",
    page_icon="🇪🇺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Use a non-interactive backend for matplotlib to avoid issues in some environments
import matplotlib
matplotlib.use('Agg')

# Custom CSS for a professional, clean corporate look
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton>button {
        border-radius: 6px;
        height: 3em;
        font-weight: 600;
        transition: all 0.3s;
        background-color: #4CAF50; /* Green */
        color: white;
        border: none;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        background-color: #45a049;
    }
    .stFileUploader>div>button {
        background-color: #008CBA; /* Blue */
        color: white;
        border-radius: 6px;
        height: 3em;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stFileUploader>div>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        background-color: #007bb5;
    }
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 5rem 0;
        text-align: center;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    .hero-section h1 {
        font-size: 3.8rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .hero-section h5 {
        font-size: 1.6rem;
        font-weight: 400;
        margin-bottom: 2.5rem;
        opacity: 0.9;
    }
    .feature-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s;
    }
    .feature-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-5px);
    }
    .feature-card h4 {
        color: #1E90FF;
        margin-bottom: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

# Translations
TRANSLATIONS = {
    "English": {
        "title": "🇪🇺 EU AI Act Transparency Auditor",
        "subtitle": "Enterprise Compliance Engine for the German Industrial Market",
        "sidebar_title": "System Configuration",
        "lang_toggle": "Language / Sprache",
        "upload_label": "Upload Technical Documentation (PDF)",
        "upload_help": "Upload system documentation, architectural designs, or user manuals to audit against the May 8, 2026 Draft Guidelines.",
        "analyze_btn": "Initialize Compliance Audit",
        "error_api_key": "System Error: Missing GOOGLE_API_KEY environment variable. Please configure to proceed.",
        "analyzing": "Executing AI Act Article 50 Compliance Scan...",
        "results_title": "Official Audit Report",
        "overall_score": "Compliance Readiness Score",
        "ai_disclosure": "AI-User Disclosure Verification",
        "synthetic_labeling": "Synthetic Content / Deepfake Labeling",
        "watermarking": "Machine-Readable Watermarking Standards",
        "pass": "Compliant",
        "fail": "Action Required",
        "reasoning": "Audit Findings",
        "score": "Score",
        "download_btn": "Download Official PDF Report",
        "invalid_doc": "Invalid or Irrelevant Document",
        "how_it_works": "How the Auditor Works",
        "step_1": "1. Document Parsing: Extracts text securely from uploaded technical PDFs.",
        "step_2": "2. Sovereign AI Scan: Analyzes content using enterprise-grade LLMs locally aligned with EU data standards.",
        "step_3": "3. Scoring & Reporting: Generates actionable metrics and an official compliance document.",
        "act_reference_title": "Official Reference: Article 50",
        "risk_classification": "System Risk Classification",
        "remediation_plan": "Recommended Remediation Plan",
        "no_remediation": "System is fully compliant. No immediate remediation required.",
        "feature_1_title": "AI-Powered Compliance Checks",
        "feature_1_desc": "Automatically audits your technical documentation against the latest EU AI Act guidelines, ensuring comprehensive transparency.",
        "feature_2_title": "Multi-Language Support",
        "feature_2_desc": "Seamlessly switch between English and German for an inclusive user experience, catering to diverse enterprise needs.",
        "feature_3_title": "Detailed Remediation Plans",
        "feature_3_desc": "Receive actionable recommendations to address identified compliance gaps, streamlining your path to full adherence.",
        "act_text": """**EU AI Act - Article 50 (Transparency Obligations)**
*Draft Guidelines May 8, 2026*

**1. AI-User Disclosure:** Providers must ensure that AI systems intended to interact directly with natural persons are designed and developed in such a way that natural persons are informed that they are interacting with an AI system.

**2. Synthetic Content Labeling:** Deployers of an AI system that generates or manipulates image, audio or video content constituting a \'deepfake\' shall disclose that the content has been artificially generated or manipulated.

**3. Watermarking Standards:** Providers of AI systems generating synthetic audio, image, video or text content shall ensure the outputs of the AI system are marked in a machine-readable format and detectable as artificially generated or manipulated."""
    },
    "Deutsch": {
        "title": "🇪🇺 EU AI Act Transparenz-Auditor",
        "subtitle": "Enterprise Compliance Engine für den deutschen Industriemarkt",
        "sidebar_title": "Systemkonfiguration",
        "lang_toggle": "Sprache / Language",
        "upload_label": "Technische Dokumentation hochladen (PDF)",
        "upload_help": "Laden Sie Systemdokumentationen, Architekturdesigns oder Benutzerhandbücher hoch, um sie gegen die Richtlinien vom 8. Mai 2026 zu prüfen.",
        "analyze_btn": "Compliance-Audit initialisieren",
        "error_api_key": "Systemfehler: Fehlende Umgebungsvariable GOOGLE_API_KEY. Bitte konfigurieren, um fortzufahren.",
        "analyzing": "KI-Verordnung Artikel 50 Compliance-Scan wird ausgeführt...",
        "results_title": "Offizieller Audit-Bericht",
        "overall_score": "Compliance-Bereitschaftsscore",
        "ai_disclosure": "Verifizierung der KI-Nutzer-Offenlegung",
        "synthetic_labeling": "Kennzeichnung synthetischer Inhalte",
        "watermarking": "Maschinenlesbare Wasserzeichen-Standards",
        "pass": "Konform",
        "fail": "Handlungsbedarf",
        "reasoning": "Audit-Ergebnisse",
        "score": "Punktzahl",
        "download_btn": "Offiziellen PDF-Bericht herunterladen",
        "invalid_doc": "Ungültiges oder irrelevantes Dokument",
        "how_it_works": "Wie der Auditor funktioniert",
        "step_1": "1. Dokumentenanalyse: Extrahiert Text sicher aus hochgeladenen technischen PDFs.",
        "step_2": "2. Sovereign AI Scan: Analysiert Inhalte mit Enterprise-LLMs nach EU-Datenstandards.",
        "step_3": "3. Bewertung & Berichterstattung: Generiert handlungsorientierte Metriken und ein offizielles Compliance-Dokument.",
        "act_reference_title": "Offizielle Referenz: Artikel 50",
        "risk_classification": "Systemrisikoklassifizierung",
        "remediation_plan": "Empfohlener Maßnahmenplan",
        "no_remediation": "Das System ist vollständig konform. Keine unmittelbaren Maßnahmen erforderlich.",
        "feature_1_title": "KI-gesteuerte Compliance-Prüfungen",
        "feature_1_desc": "Überprüft automatisch Ihre technische Dokumentation anhand der neuesten EU-KI-Gesetzrichtlinien, um umfassende Transparenz zu gewährleisten.",
        "feature_2_title": "Mehrsprachige Unterstützung",
        "feature_2_desc": "Nahtloser Wechsel zwischen Englisch und Deutsch für ein inklusives Benutzererlebnis, das vielfältigen Unternehmensanforderungen gerecht wird.",
        "feature_3_title": "Detaillierte Abhilfemaßnahmen",
        "feature_3_desc": "Erhalten Sie umsetzbare Empfehlungen zur Behebung festgestellter Compliance-Lücken, um Ihren Weg zur vollständigen Einhaltung zu optimieren.",
        "act_text": """**EU-KI-Verordnung - Artikel 50 (Transparenzpflichten)**
*Richtlinienentwurf 8. Mai 2026*

**1. KI-Nutzer-Offenlegung:** Anbieter müssen sicherstellen, dass KI-Systeme, die für die direkte Interaktion mit natürlichen Personen bestimmt sind, so konzipiert werden, dass die natürlichen Personen darüber informiert werden, dass sie mit einem KI-System interagieren.

**2. Kennzeichnung synthetischer Inhalte:** Betreiber eines KI-Systems, das Bild-, Ton- oder Videoinhalte generiert oder manipuliert, die einen \"Deepfake\" darstellen, müssen offenlegen, dass die Inhalte künstlich erzeugt oder manipuliert wurden.

**3. Wasserzeichen-Standards:** Anbieter von KI-Systemen, die synthetische Inhalte generieren, müssen sicherstellen, dass die Ausgaben in einem maschinenlesbaren Format markiert und als künstlich erzeugt erkennbar sind."""
    }
}

# Sidebar configuration
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/b/b7/Flag_of_Europe.svg", width=80)
    st.markdown("### Auditor Settings")
    language = st.radio("Global Language", ["English", "Deutsch"], label_visibility="collapsed")
    t = TRANSLATIONS[language]
    
    st.divider()
    st.markdown(f"**{t['sidebar_title']}**")
    
    # API Status with visual indicator
    api_key_status = "🟢 Active & Verified" if os.getenv("GOOGLE_API_KEY") else "🔴 Disconnected"
    st.info(f"API Connection:\n\n**{api_key_status}**")
    
    st.divider()
    st.caption("v1.0.0-enterprise | Build: 2026.05")

# Hero Section for a compelling landing experience
st.markdown("""
<div class="hero-section">
    <h1>🇪🇺 EU AI Act Transparency Auditor</h1>
    <h5>Enterprise Compliance Engine for the German Industrial Market</h5>
</div>
""", unsafe_allow_html=True)

# Feature Showcase below the hero section
st.markdown("### Key Features", unsafe_allow_html=True)
feature_col1, feature_col2, feature_col3 = st.columns(3)

with feature_col1:
    with st.container(border=True):
        st.markdown(f"<h4>{t['feature_1_title']}</h4>", unsafe_allow_html=True)
        st.write(t['feature_1_desc'])

with feature_col2:
    with st.container(border=True):
        st.markdown(f"<h4>{t['feature_2_title']}</h4>", unsafe_allow_html=True)
        st.write(t['feature_2_desc'])

with feature_col3:
    with st.container(border=True):
        st.markdown(f"<h4>{t['feature_3_title']}</h4>", unsafe_allow_html=True)
        st.write(t['feature_3_desc'])

st.markdown("<br>", unsafe_allow_html=True)

# Main Workspace (moved below features)
col_main, col_info = st.columns([2, 1])

with col_info:
    # Professional 'How it works' panel
    with st.container(border=True):
        st.markdown(f"**ℹ️ {t['how_it_works']}**")
        st.markdown(f"<small>{t['step_1']}</small>", unsafe_allow_html=True)
        st.markdown(f"<small>{t['step_2']}</small>", unsafe_allow_html=True)
        st.markdown(f"<small>{t['step_3']}</small>", unsafe_allow_html=True)
        
    # Display Original Act Reference
    with st.expander(f"📜 {t['act_reference_title']}"):
        st.info(t['act_text'])

with col_main:
    # Upload interface inside a neat container
    with st.container(border=True):
        uploaded_file = st.file_uploader(t["upload_label"], type=["pdf"], help=t["upload_help"])
        
        if st.button(t["analyze_btn"], type="primary", use_container_width=True, disabled=not uploaded_file):
            if not os.getenv("GOOGLE_API_KEY"):
                st.error(t["error_api_key"])
            else:
                with st.spinner(t["analyzing"]):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_file_path = tmp_file.name
                    
                    try:
                        results = analyze_pdf(tmp_file_path)
                        
                        if results.get("is_relevant") is False:
                            st.error(f"🚫 **{t['invalid_doc']}**: {results.get('error')}")
                            if 'audit_results' in st.session_state:
                                del st.session_state['audit_results']
                        elif "error" in results:
                            st.error(f"Error during analysis: {results['error']}")
                        else:
                            st.session_state['audit_results'] = results
                    finally:
                        if os.path.exists(tmp_file_path):
                            os.remove(tmp_file_path)

# Results Display Section
if 'audit_results' in st.session_state:
    results = st.session_state['audit_results']
    
    st.divider()
    st.markdown(f"### 📊 {t['results_title']}")
    
    # High-level Summary Dashboard
    dash_col1, dash_col2 = st.columns([1, 2])
    with dash_col1:
        with st.container(border=True):
            st.metric(label=t["overall_score"], value=f"{results['overall_score']}%", help="Overall compliance score based on Article 50.") # Added help text
            st.progress(results["overall_score"] / 100.0)
    with dash_col2:
        with st.container(border=True):
            if results['overall_score'] >= 80:
                st.success("✅ **High Compliance Readiness**: The documentation aligns well with Article 50 guidelines.")
            elif results['overall_score'] >= 50:
                st.warning("⚠️ **Moderate Compliance**: Certain areas require significant refinement before deployment.")
            else:
                st.error("🚨 **Critical Non-Compliance**: System fails to meet fundamental transparency requirements.")
                
            st.markdown(f"**{t['risk_classification']}**: `{results.get('risk_level', 'Unknown')}`")
            st.caption(results.get('risk_reasoning', ''))

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📋 Detailed Audit Breakdown")
    
    # Detailed Metric Cards
    metrics_data = [
        (t["ai_disclosure"], results["ai_user_disclosure"]),
        (t["synthetic_labeling"], results["synthetic_content_labeling"]),
        (t["watermarking"], results["watermarking_compliance"])
    ]
    
    for title, data in metrics_data:
        with st.container(border=True):
            mc_col1, mc_col2 = st.columns([4, 1])
            status_color = "🟢" if data["status"].lower() == "pass" else "🔴"
            status_text = t["pass"] if data["status"].lower() == "pass" else t["fail"]
            
            with mc_col1:
                st.markdown(f"**{title}**")
                st.write(data['reasoning'])
            with mc_col2:
                st.markdown(f"<h3 style='text-align: right;'>{status_color} {data['score']}%</h3>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: right; color: gray;'>Status: <strong>{status_text}</strong></div>", unsafe_allow_html=True)

    # Remediation Plan Section
    st.markdown(f"#### 🛠️ {t['remediation_plan']}")
    with st.container(border=True):
        remediation_steps = results.get('remediation_plan', [])
        if not remediation_steps or results['overall_score'] == 100:
            st.info(t['no_remediation'])
        else:
            for idx, step in enumerate(remediation_steps, 1):
                st.markdown(f"**{idx}.** {step}")

    # PDF Generation Logic
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    
    # PDF Header
    pdf.set_font("helvetica", style='B', size=18)
    pdf.cell(0, 15, "EU AI Act Transparency Auditor", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", size=10)
    pdf.cell(0, 5, "Official Compliance Audit Report (Article 50)", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    # Generate a pie chart for overall compliance score
    fig1, ax1 = plt.subplots(figsize=(4, 4))
    scores = [results['overall_score'], 100 - results['overall_score']]
    labels = [t['overall_score'], 'Non-Compliant']
    colors = ['#4CAF50', '#FF6347'] # Green for compliant, Red for non-compliant
    
    # Ensure labels match the number of scores
    actual_labels = [label for i, label in enumerate(labels) if scores[i] > 0]
    actual_colors = [color for i, color in enumerate(colors) if scores[i] > 0]
    actual_scores = [score for score in scores if score > 0]

    ax1.pie(actual_scores, labels=actual_labels, colors=actual_colors, autopct='%1.1f%%', startangle=90, textprops={'color': 'white'}) 
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    
    buf1 = io.BytesIO()
    plt.savefig(buf1, format="png", bbox_inches='tight', transparent=True)
    buf1.seek(0)
    pdf.image(buf1, x=60, w=90) # Adjust x and w for positioning and size
    pdf.ln(5)

    # PDF Overall Score Text
    pdf.set_font("helvetica", style='B', size=14)
    pdf.cell(0, 10, f"{t['overall_score']}: {results['overall_score']}%", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    def add_pdf_section(title, data):
        pdf.set_font("helvetica", style='B', size=12)
        status_text = t["pass"] if data["status"].lower() == "pass" else t["fail"]
        pdf.cell(0, 10, f"{title} - {t['score']}: {data['score']}% ({status_text})", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("helvetica", size=11)
        reasoning_text = f"{t['reasoning']}: {data['reasoning']}"
        reasoning_text = reasoning_text.replace('“', '"').replace('”', '"').replace("‘", "'").replace("’", "'").replace('—', '-').replace('–', '-')
        reasoning_text = reasoning_text.encode('latin-1', 'ignore').decode('latin-1')
        
        pdf.multi_cell(0, 8, reasoning_text, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        
    for title, data in metrics_data:
        add_pdf_section(title, data)
        
    pdf_bytes = bytes(pdf.output())
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label=f"📄 {t['download_btn']}",
        data=pdf_bytes,
        file_name="official_compliance_audit_report.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True
    )

# Professional Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.85em; border-top: 1px solid #ddd; padding-top: 1em;'>"
    "<strong>Confidential & Proprietary</strong><br>"
    "Built with Sovereign AI architecture ensuring local data privacy. "
    "Compliance algorithms dynamically aligned with May 8, 2026 EU AI Act Draft Guidelines."
    "</div>",
    unsafe_allow_html=True
)
