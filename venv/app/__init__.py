from flask import Flask
import google.generativeai as genai
from app.routes import bp

# Configure the Generative AI API key
genai.configure(api_key="AIzaSyCxgKo5NcdNFLRsdenH3vny_dMiEFszfjo")

def create_app():
    # Initialize the app (You don’t need Gemini here, as we're using Google's generative AI directly)
    app = Flask(__name__)

    # Configurations
    app.config["UPLOAD_FOLDER"] = "uploads"
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

    # Register Blueprint
    app.register_blueprint(bp)

    return app
