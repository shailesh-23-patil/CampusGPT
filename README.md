# CampusGPT

CampusGPT is an AI-powered academic assistant designed for students who want to upload study material and ask questions directly from their documents. It uses a Retrieval-Augmented Generation (RAG) workflow with Gemini AI, PDF text extraction, chunking, vector search, and answer generation to provide context-aware responses based on the uploaded content.

## Overview

This project helps students:

- Upload one or more PDF notes
- Extract and index study content automatically
- Ask questions in natural language
- Get answers grounded in the uploaded documents
- View source references with page numbers for better trust and transparency

It is especially useful for revision, quick doubt clarification, and exam preparation from handwritten or digital notes shared in PDF format.

## Features

- PDF upload and text extraction
- Intelligent chunking of study material
- Embedding generation using Gemini models
- FAISS similarity search for relevant document retrieval
- Context-aware question answering through Gemini
- Session-based chat history for follow-up questions
- Source citation with file and page details
- Simple Flask-based web interface

## Tech Stack

- Python
- Flask
- FAISS
- NumPy
- pypdf
- Google Gemini API
- HTML/CSS/JavaScript

## Project Structure

```text
CampusGPT_Minor_Project/
├── app.py                  # Main Flask application
├── app_streamlit_backup.py # Backup/alternative Streamlit version
├── generate_notes.py       # Utility script for generating note PDFs
├── CampusGPT.ipynb        # Jupyter exploration notebook
├── Notes/                 # Generated or sample notes
├── static/                # CSS and JavaScript assets
├── templates/             # HTML templates
└── README.md              # Project documentation
```

## Prerequisites

Before running the project, make sure you have:

- Python 3.9 or newer
- A valid Google Gemini API key
- A working internet connection for AI API calls

## Installation

1. Open a terminal in the project folder.

2. Create a virtual environment:

```bash
python -m venv .venv
```

3. Activate the virtual environment:

On Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

4. Install the required packages:

```bash
pip install flask numpy faiss-cpu pypdf google-genai reportlab
```

## Running the Application

Start the Flask app:

```bash
python app.py
```

Then open this in your browser:

```text
http://127.0.0.1:5001
```

## How to Use

1. Enter your Gemini API key in the app.
2. Upload one or more PDF study files.
3. Wait for the files to be processed and indexed.
4. Ask questions related to the documents.
5. Review the answer along with the cited source and page information.

## Notes on the AI Workflow

The application works in this flow:

1. PDF content is extracted page by page.
2. The text is split into smaller chunks.
3. Each chunk is converted into embeddings.
4. Similar chunks are retrieved based on the user question.
5. Gemini generates a final answer using only the relevant document context.

This keeps the response focused on the uploaded material instead of guessing from general knowledge.

## Important Configuration

The project currently uses a placeholder secret key in the Flask app:

```python
app.secret_key = 'replace-with-strong-secret-key'
```

For a real deployment, replace it with a secure secret value. In production, it is recommended to store sensitive values in environment variables instead of hardcoding them.

## Common Issues

### API key problem
If you see a Gemini connection error:

- Check whether the key is valid
- Ensure you have access to the Gemini API
- Confirm your account quota is available

### No text found in PDF
If the uploaded file does not get processed:

- Make sure the file is a valid PDF
- Ensure the PDF contains readable text
- Try a different document if it is scanned or image-based

### Quota or service errors
If Gemini returns a 429 or temporary unavailable response:

- Wait and retry later
- Check your API usage limits
- Ensure the project is not making excessive requests

## Optional Utility Script

The repository includes a helper script named `generate_notes.py` to generate educational note PDFs. This is useful for building or testing sample study materials for the app.

## License

This project is intended for educational and learning purposes. Please check your local usage and distribution requirements before sharing it publicly or using it in a commercial setting.

## Future Improvements

Possible enhancements include:

- Support for DOCX and TXT files
- Better UI/UX improvements
- Chat history persistence
- User authentication
- PDF export of generated study notes
- Better handling of scanned PDFs and image-based documents

## Conclusion

CampusGPT is a practical AI study assistant that turns uploaded PDFs into an interactive learning experience. It is simple to run, beginner-friendly, and designed to help students learn faster with context-grounded answers.

If you want, I can also create a more polished version with:

- a project logo section
- a screenshot-ready homepage description
- a badges section
- a detailed installation guide for Windows users
- a shorter GitHub-style README version
