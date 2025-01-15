import os
import logging
from flask import Blueprint, request, jsonify, render_template
from app.models.resume_parser import parse_resume
from app.models.jd_parser import parse_jd
from app.models.summarizer import summarize_resume
from app.models.scorer import score_resume
from app.models.question_gen import generate_questions
from PyPDF2 import PdfReader
from docx import Document
import uuid

# Set up logging
logging.basicConfig(level=logging.DEBUG)

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

bp = Blueprint("routes", __name__)

# Ensure the uploads directory exists
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Route to display the HTML form
@bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Route to handle file and job description upload
@bp.route("/upload", methods=["POST"])
def upload_resume():
    job_description = request.form.get("job_description")
    
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file format. Please upload a PDF, DOCX, or TXT file."}), 400

    if file:
        # Generate unique filename and save the file
        filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        if not job_description:
            return jsonify({"error": "Job description is required"}), 400

        try:
            # Debugging step: Check the raw content of the uploaded file
            with open(file_path, "rb") as f:
                file_content = f.read()
                logging.debug(f"Raw file content (first 500 bytes): {file_content[:500]}")

            # Parse resume content
            resume_content = parse_resume(file_path)
            logging.debug(f"Parsed Resume content: {resume_content}")

            if not resume_content:
                return jsonify({"error": "No content extracted from the resume."}), 400

            # Parse job description
            jd_content = parse_jd(job_description)
            logging.debug(f"Parsed Job Description: {jd_content}")

            if not jd_content:
                return jsonify({"error": "No content extracted from job description."}), 400

            # Summarize resume
            summary = summarize_resume(resume_content)
            logging.debug(f"Summary generated: {summary}")

            # Score the resume
            score, alignment = score_resume(summary, jd_content)
            logging.debug(f"Resume Score: {score}, Alignment: {alignment}")

            # Generate questions if alignment is sufficient
            questions = []
            if alignment >= 60:
                questions = generate_questions(resume_content, jd_content)
                logging.debug(f"Generated questions: {questions}")

            # Return response
            return jsonify({
                "summary": summary,
                "score": score,
                "alignment": alignment,
                "questions": questions,
            })

        except Exception as e:
            logging.error(f"Error processing the resume: {str(e)}")
            return jsonify({"error": f"Error processing the resume: {str(e)}"}), 500

    return jsonify({"error": "Invalid file format"}), 400
