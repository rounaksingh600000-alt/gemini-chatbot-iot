# Arduino IoT Chatbot (Streamlit + Gemini)

## Setup
1. (Optional) create a virtual environment:
   python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
2. Install dependencies:
   pip install -r requirements.txt
3. Open `.streamlit/secrets.toml` and paste your Gemini API key.
4. Run:
   streamlit run app.py

## Files
- app.py                      Streamlit app
- requirements.txt            Dependencies
- .streamlit/secrets.toml     API key + model name (keep private)
- .gitignore                  Keeps secrets out of git
