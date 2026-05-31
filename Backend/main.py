from services.qa_engine import ask_meeting_ai
from pydantic import BaseModel
from services.transcriber import transcribe_audio
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):

    contents = await file.read()

    UPLOAD_FOLDER = "uploads"

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    file_path = os.path.join(UPLOAD_FOLDER, "meeting_audio.wav")

    with open(file_path, "wb") as f:
        f.write(contents)

    transcript = transcribe_audio(file_path)
    os.makedirs("transcripts", exist_ok=True)

    with open(
        "transcripts/transcript.txt",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(transcript)

    return {
        "message": "Audio uploaded successfully",
        "transcript": transcript
    }

@app.get("/transcript")
def get_transcript():

    with open(
        "transcripts/transcript.txt",
        "r",
        encoding="utf-8"
    ) as f:

        transcript = f.read()

    return {
        "transcript": transcript
    }
@app.post("/ask-ai")
def ask_ai(request: QuestionRequest):

    with open(
        "transcripts/transcript.txt",
        "r",
        encoding="utf-8"
    ) as f:

        transcript = f.read()

    answer = ask_meeting_ai(
        transcript,
        request.question
    )

    return {
        "answer": answer
    }