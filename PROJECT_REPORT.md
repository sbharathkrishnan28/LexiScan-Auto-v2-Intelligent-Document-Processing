# Intern Project Report: Fintech Intelligent Document Processing

## Executive Summary
This project successfully demonstrates the application of Natural Language Processing (NLP) to automate the tedious and error-prone task of reviewing legal contracts. By leveraging a custom NLP pipeline and a modern web interface, LexiScan Auto drastically reduces document review times while enhancing data privacy.

## Problem Statement
A large financial law firm manages millions of PDF contracts. Manual review to find standard entities (Parties, Values, Dates) is slow. The firm required a system to automatically extract these key structured entities and index the documents for searchability.

## Solution Implemented
I developed a full-stack web application that allows users to drag-and-drop contracts into a dashboard. The system instantly analyzes the text, extracts the required entities, and provides a real-time, privacy-compliant preview of the document.

### Key Features & Innovations
1. **Real-Time NLP Engine**: Utilized `Spacy` and `PyMuPDF` to achieve millisecond-level extraction times.
2. **Automated PII Redaction**: Added a unique data-privacy layer that automatically masks sensitive names and financial figures, ensuring compliance with data protection regulations like GDPR.
3. **Human-in-the-Loop Safeguards**: Engineered a confidence scoring system that flags documents requiring manual legal review if the AI fails to find core entities.
4. **Premium UI/UX**: Designed a modern "Glassmorphism" React dashboard to present the complex AI data in a user-friendly, highly visual manner.

## Future Scope
*   Integrate a large language model (LLM) like GPT-4 or Gemini to extract complex, non-standard clauses.
*   Deploy the application to AWS using Docker containers and ECS.
*   Replace SQLite with Elasticsearch for advanced, fuzzy document querying.
