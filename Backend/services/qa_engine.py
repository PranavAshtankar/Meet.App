import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
import os


genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-2.5-flash")

def ask_meeting_ai(transcript, question):

    prompt = f"""
    You are an AI meeting assistant.

    Meeting Transcript:
    {transcript}

    User Question:
    {question}

    Answer only from the meeting transcript.
    If the answer is not present, say:
    'This was not discussed in the meeting.'
    """

    try:
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Gemini Error: {str(e)}"