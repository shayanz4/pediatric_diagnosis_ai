# Pediatric Diagnosis AI

An AI-powered diagnostic system for pediatric conditions that uses Prolog rules and natural language processing to help identify possible diagnoses based on reported symptoms.

## Overview

This system provides two modes of interaction:
- **Normal Mode**: A structured checklist-based approach where users select symptoms from predefined lists
- **DCG Mode**: A natural language processing approach where users can describe symptoms in free text

The diagnostic process works in three tiers:
1. **Tier 1**: Initial symptom identification
2. **Tier 2**: Detailed symptom characterization
3. **Tier 3**: Disease-specific differential questions

## Features

- Web-based interface built with FastAPI and Jinja2 templates
- Prolog-based diagnostic reasoning engine
- Natural language processing for symptom extraction
- Probability-based diagnosis suggestions
- Recommended department referrals

## Setup

### Prerequisites

- Python 3.8+
- SWI-Prolog (must be installed and accessible in path)
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pediatric_diagnosis_ai.git
cd pediatric_diagnosis_ai
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install fastapi uvicorn jinja2 python-multipart pyswip
```

4. Make sure SWI-Prolog is installed on your system

### Running the Application

Start the web server:
```bash
python app.py
```

Access the web interface at: http://localhost:8000

## Usage

### Normal Mode

1. Select primary symptoms from the checklist
2. Provide detailed information about each selected symptom
3. Answer follow-up questions if prompted
4. View the diagnostic results

### DCG Mode (Natural Language)

1. Describe all observed symptoms in natural language
2. Provide detailed information about detected symptoms
3. Answer follow-up questions if prompted
4. View the diagnostic results

## Technical Details

### Architecture

- **Frontend**: HTML/JavaScript with Jinja2 templates
- **Backend**: FastAPI Python server
- **Reasoning Engine**: SWI-Prolog with PySwip integration

### Knowledge Base

The diagnostic knowledge is stored in Prolog files:
- `diagnosis.pl`: Contains rules for regular symptom mode
- `dcg_rules.pl`: Contains DCG grammar for natural language parsing and additional diagnostic rules

### Components

- **DiagnosisEngine**: Core class that interfaces with Prolog
- **FastAPI Routes**: Handle HTTP requests and responses
- **Prolog Predicates**: Define the diagnostic logic

## Limitations

- The system provides suggestions only and should not replace professional medical advice
- Diagnosis accuracy depends on the completeness of the knowledge base
- Natural language processing has limitations in understanding complex symptom descriptions

## Future Improvements

- Expand the knowledge base with more pediatric conditions
- Improve natural language understanding capabilities
- Add integration with electronic health records
- Implement machine learning to improve diagnostic accuracy over time

## License

This project is licensed under the MIT License - see the LICENSE file for details.
