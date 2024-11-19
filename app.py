from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as gemini
import PyPDF2
from docx import Document
import io

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Set your Gemini API key
gemini.configure(api_key="AIzaSyAyOZe2x8MZAP7Ly1HG2n6vkriESBA-KUM")

def extract_text_from_pdf(file):
    """Extract text from a PDF file."""
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file):
    """Extract text from a DOCX file."""
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

@app.route("/analyze-resume", methods=["POST"])
def analyze_resume():
    if "resume" not in request.files:
        return jsonify({"error": "No resume file uploaded."}), 400

    resume_file = request.files["resume"]
    question = request.form.get("question")

    if not question:
        return jsonify({"error": "No question provided."}), 400

    try:
        # Extract text based on file type
        if resume_file.filename.endswith(".pdf"):
            resume_text = extract_text_from_pdf(resume_file.stream)
        elif resume_file.filename.endswith(".docx"):
            resume_text = extract_text_from_docx(resume_file.stream)
        else:
            return jsonify({"error": "Unsupported file format. Please upload a PDF or DOCX file."}), 400

        # Query the Gemini API
        response = gemini.generate_text(
            prompt=f"Analyze the following resume:\n{resume_text}\n\nQuestion: {question}",
            temperature=0.7,
        )

        # Process the response
        answer = response.result or "No specific answer provided."
        suggestions = "Consider emphasizing key achievements, skills, and tailoring the resume for the intended role."

        return jsonify({"answer": answer, "suggestions": suggestions})

    except Exception as e:
        print(e)
        return jsonify({"error": "An error occurred while processing the resume."}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
