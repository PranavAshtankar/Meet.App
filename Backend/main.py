from services.qa_engine import ask_meeting_ai
from pydantic import BaseModel
from services.transcriber import transcribe_audio
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST = os.path.abspath(
    os.path.join(BASE_DIR, "..", "meeting-ai", "dist")
)

class QuestionRequest(BaseModel):
    question: str

frontend_origin = os.getenv("FRONTEND_ORIGIN", "*")
allowed_origins = (
    ["*"]
    if frontend_origin == "*"
    else [origin.strip() for origin in frontend_origin.split(",")]
)

# Allow frontend requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

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

if os.path.isdir(FRONTEND_DIST):
    assets_dir = os.path.join(FRONTEND_DIST, "assets")

    if os.path.isdir(assets_dir):
        app.mount(
            "/assets",
            StaticFiles(directory=assets_dir),
            name="assets"
        )

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        requested_path = os.path.join(FRONTEND_DIST, full_path)

        if full_path and os.path.isfile(requested_path):
            return FileResponse(requested_path)

        return FileResponse(
            os.path.join(FRONTEND_DIST, "index.html")
        )
