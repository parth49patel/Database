from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as gemini
import PyPDF2
from docx import Document
import io
from io import BytesIO
import logging

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Set your Gemini API key
gemini.configure(api_key="")

# Enable logging
logging.basicConfig(level=logging.DEBUG)


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


def create_new_resume(original_text, answer, suggestions):
    """Create a new resume text by appending answers and suggestions."""
    new_resume = (
        f"{original_text}\n\nAnalysis:\n{answer}\n\nSuggestions:\n{suggestions}"
    )
    return new_resume


def generate_pdf_from_text(text):
    """Generate a PDF from the text to send back to the client."""
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output


@app.route("/analyze-resume", methods=["POST"])
def analyze_resume():
    if "resume" not in request.files:
        logging.error("No resume file uploaded.")
        return jsonify({"error": "No resume file uploaded."}), 400

    resume_file = request.files["resume"]
    question = request.form.get("question")

    if not question:
        logging.error("No question provided.")
        return jsonify({"error": "No question provided."}), 400

    try:
        # Extract text based on file type
        if resume_file.filename.endswith(".pdf"):
            resume_text = extract_text_from_pdf(resume_file.stream)
        elif resume_file.filename.endswith(".docx"):
            resume_text = extract_text_from_docx(resume_file.stream)
        else:
            logging.error("Unsupported file format.")
            return (
                jsonify(
                    {
                        "error": "Unsupported file format. Please upload a PDF or DOCX file."
                    }
                ),
                400,
            )

        # Log the extracted resume text for debugging
        logging.debug(
            f"Extracted resume text: {resume_text[:500]}..."
        )  # Print first 500 characters of text

        # Query the Gemini API
        response = gemini.generate_text(
            prompt=f"Analyze the following resume:\n{resume_text}\n\nQuestion: {question}",
            temperature=0.7,
        )

        # Check the response and log errors
        if not response or not hasattr(response, "result"):
            logging.error("Failed to generate response from Gemini.")
            return (
                jsonify({"error": "Error processing the resume with Gemini API."}),
                500,
            )

        answer = response.result or "No specific answer provided."
        suggestions = "Consider emphasizing key achievements, skills, and tailoring the resume for the intended role."

        # Log the generated answer and suggestions for debugging
        logging.debug(f"Generated answer: {answer}")
        logging.debug(f"Suggestions: {suggestions}")

        # Create the new resume with added answers and suggestions
        new_resume_text = create_new_resume(resume_text, answer, suggestions)

        # Generate a new PDF with the new resume content
        new_resume_pdf = generate_pdf_from_text(new_resume_text)

        # Return the PDF as a downloadable response
        return (
            jsonify({"message": "Resume analyzed successfully!"}),
            200,
            {
                "Content-Type": "application/pdf",
                "Content-Disposition": "attachment; filename=analyzed_resume.pdf",
            },
        )

    except Exception as e:
        logging.exception("An error occurred while processing the resume.")
        return jsonify({"error": "An error occurred while processing the resume."}), 500


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
