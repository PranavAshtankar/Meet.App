import { useRef, useState } from "react";

export default function App() {
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const [isRecording, setIsRecording] = useState(false);
  const [audioURL, setAudioURL] = useState("");
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState("");
  const [transcript, setTranscript] = useState("");

  const startRecording = async () => {
  try {
    const screenStream =
      await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: true,
      });

    const micStream =
      await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

    const audioContext = new AudioContext();
    const destination =
      audioContext.createMediaStreamDestination();

    if (screenStream.getAudioTracks().length > 0) {
      const screenSource =
        audioContext.createMediaStreamSource(
          screenStream
        );

      screenSource.connect(destination);
    }

    const micSource =
      audioContext.createMediaStreamSource(
        micStream
      );

    micSource.connect(destination);

    const combinedStream =
      destination.stream;

    const mediaRecorder =
      new MediaRecorder(combinedStream);

    mediaRecorderRef.current = mediaRecorder;
    audioChunksRef.current = [];

    mediaRecorder.ondataavailable = (event) => {
      audioChunksRef.current.push(event.data);
    };

    mediaRecorder.onstart = () => {
      setIsRecording(true);
    };

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(
        audioChunksRef.current,
        {
          type: mediaRecorder.mimeType,
        }
      );

      const audioUrl =
        URL.createObjectURL(audioBlob);

      setAudioURL(audioUrl);

      const formData = new FormData();

      formData.append(
        "file",
        audioBlob,
        "meeting_audio.webm"
      );

      try {
        const response = await fetch(
          "http://127.0.0.1:8000/upload-audio",
          {
            method: "POST",
            body: formData,
          }
        );

        const data =
          await response.json();

        setTranscript(data.transcript);
      } catch (error) {
        console.error(
          "Upload failed:",
          error
        );
      }

      setIsRecording(false);
    };

    mediaRecorder.start();

  } catch (error) {
    console.error(
      "Recording failed:",
      error
    );
  }
};


  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }
  };

  const askAI = async () => {
    try {
      const res = await fetch(
        "http://127.0.0.1:8000/ask-ai",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: question,
          }),
        }
      );

      const data = await res.json();

      setResponse(data.answer);

    } catch (error) {
      console.error(error);
      setResponse("Error contacting AI.");
    }
  };

  return (
    <div style={{ padding: "40px", fontFamily: "Arial" }}>
      <h1>AI Meeting Assistant</h1>

      <button onClick={startRecording} disabled={isRecording}>
        Start Recording
      </button>

      <button
        onClick={stopRecording}
        disabled={!isRecording}
        style={{ marginLeft: "10px" }}
      >
        Stop Recording
      </button>

      <p>
        Status: {isRecording ? "🎤 Recording..." : "Idle"}
      </p>

      {audioURL && (
        <div>
          <h3>Recorded Audio:</h3>

          <audio controls src={audioURL}></audio>
          {transcript && (
            <div style={{ marginTop: "20px" }}>
              <h3>Transcript:</h3>
              <p>{transcript}</p>
            </div>
          )}
        </div>
      )}

      <div style={{ marginTop: "20px" }}>
        <input
          type="text"
          placeholder="Ask AI about meeting"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          style={{
            padding: "10px",
            width: "300px",
          }}
        />

        <button
          onClick={askAI}
          style={{ marginLeft: "10px" }}
        >
          Ask AI
        </button>
      </div>

      {response && (
        <div style={{ marginTop: "20px" }}>
          <h3>AI Response:</h3>
          <p>{response}</p>
        </div>
      )}
    </div>
  );
}