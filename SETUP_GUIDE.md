# Environment Setup Guide

This guide provides instructions on how to set up the LexiScan application on a fresh Windows, Mac, or Linux machine.

## Prerequisites
*   Python 3.9+
*   Node.js v18+
*   Git

## Backend Installation

1. **Navigate to the root directory**:
   ```bash
   cd "Zaalima Intern Project 3"
   ```

2. **Create a Virtual Environment (Optional but Recommended)**:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   # source venv/bin/activate    # On Mac/Linux
   ```

3. **Install Python Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Download the NLP Model**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Start the API Server**:
   ```bash
   python -m uvicorn backend.main:app --reload --port 8000
   ```

## Frontend Installation

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node Modules**:
   ```bash
   npm install
   ```

3. **Start the Development Server**:
   ```bash
   npm run dev
   ```

Your application is now fully functional and accessible at `http://localhost:5173`.
