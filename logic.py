import os
import json
from dotenv import load_dotenv
from haystack import Pipeline
from haystack.components.converters import PyPDFToDocument
from haystack.components.builders import PromptBuilder
from haystack_integrations.components.generators.google_ai import GoogleAIGeminiGenerator
 
load_dotenv()
 
PROMPT_TEMPLATE = """
You are a professional EU AI Act Compliance Auditor, specifically trained on the May 8, 2026 Draft Guidelines from the European Commission regarding Article 50 (Transparency & Disclosure).
Your task is to analyze the following extracted text from a technical document and assess its compliance across three key areas for the German industrial market.
 
Document Text:
{{documents[0].content}}
 
Please evaluate the text for the following based on the May 8, 2026 guidelines:
1. Presence of AI-user disclosure (Is it clear to the user that they are interacting with an AI system?).
2. Deepfake/Synthetic content labeling (Are generated outputs clearly labeled as synthetic?).
3. Compliance with the new watermarking standards (Are machine-readable watermarks mentioned/implemented according to the latest standards?).
 
Also, provide:
- A risk level (e.g., Low, Medium, High, Critical).
- A brief reasoning for the risk level.
- A remediation plan with specific steps if any compliance gaps are found.
- If the document is not a technical document or is completely irrelevant to AI systems, set "is_relevant" to false.

Respond strictly in JSON format with the following structure. Do not include any other text.
{
  "is_relevant": true,
  "ai_user_disclosure": {"status": "Pass" or "Fail", "reasoning": "...", "score": 0 to 100},
  "synthetic_content_labeling": {"status": "Pass" or "Fail", "reasoning": "...", "score": 0 to 100},
  "watermarking_compliance": {"status": "Pass" or "Fail", "reasoning": "...", "score": 0 to 100},
  "risk_level": "...",
  "risk_reasoning": "...",
  "remediation_plan": ["step 1", "step 2", ...]
}
"""
 
def get_compliance_pipeline():
    # Initialize the Gemini Generator. It expects GOOGLE_API_KEY in the environment.
    # Using gemini-2.0-flash as requested (assuming 2.5 was a typo for 2.0 or newest)
    # If 2.5 is specifically required by the user, we will use exactly that.
    generator = GoogleAIGeminiGenerator(model="gemini-2.5-flash")
    
    # Initialize PyPDF to Document converter
    pdf_converter = PyPDFToDocument()
    
    # Initialize Prompt Builder
    prompt_builder = PromptBuilder(template=PROMPT_TEMPLATE)
    
    # Build Pipeline
    pipeline = Pipeline()
    pipeline.add_component("converter", pdf_converter)
    pipeline.add_component("prompt_builder", prompt_builder)
    pipeline.add_component("llm", generator)
    
    # Connect components
    pipeline.connect("converter.documents", "prompt_builder.documents")
    pipeline.connect("prompt_builder", "llm")
    
    return pipeline
 
def analyze_pdf(file_path: str):
    pipeline = get_compliance_pipeline()
    
    try:
        results = pipeline.run({
            "converter": {"sources": [file_path]}
        })
        
        # Check if documents were extracted
        if not results.get("llm") or not results["llm"].get("replies"):
             return {"error": "No response from LLM or failed to parse PDF."}

        # Parse the JSON output from the LLM
        response_text = results["llm"]["replies"][0]
        
        # Clean up Markdown formatting if Gemini wraps the response in ```json ... ```
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].strip()
            
        try:
            parsed_result = json.loads(response_text)
        except json.JSONDecodeError:
            return {"error": f"Failed to parse LLM response as JSON: {response_text[:100]}..."}
        
        if parsed_result.get("is_relevant") is False:
            parsed_result["error"] = "The uploaded document does not appear to be a relevant technical documentation for an AI system."
            return parsed_result

        # Calculate overall compliance readiness score
        try:
            total_score = (
                parsed_result["ai_user_disclosure"]["score"] +
                parsed_result["synthetic_content_labeling"]["score"] +
                parsed_result["watermarking_compliance"]["score"]
            ) / 3
            parsed_result["overall_score"] = round(total_score, 1)
        except (KeyError, TypeError):
             parsed_result["overall_score"] = 0
             parsed_result["error"] = "Incomplete data in LLM response."

        return parsed_result
        
    except Exception as e:
        return {"error": str(e)}
