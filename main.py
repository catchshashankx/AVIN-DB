from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import sqlite3

app = FastAPI()

def init_db():
    conn = sqlite3.connect("logs.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            user_transcript TEXT NOT NULL,
            user_audio_url TEXT,
            gpt_response TEXT NOT NULL,
            gpt_audio_url TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

class ConversationLog(BaseModel):
    userId: str
    timestamp: datetime
    userTranscript: str
    userAudioUrl: str | None = None
    gptResponse: str
    gptAudioUrl: str | None = None

@app.post("/logs")
async def log_conversation(log: ConversationLog):
    try:
        conn = sqlite3.connect("logs.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO conversation_logs (
                user_id, timestamp, user_transcript, user_audio_url, gpt_response, gpt_audio_url
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            log.userId,
            log.timestamp.isoformat(),
            log.userTranscript,
            log.userAudioUrl,
            log.gptResponse,
            log.gptAudioUrl
        ))
        conn.commit()

from fastapi.responses import JSONResponse

@app.get("/logs")
def get_all_logs():
    try:
        conn = sqlite3.connect("logs.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conversation_logs")
        rows = cursor.fetchall()
        conn.close()

        logs = []
        for row in rows:
            logs.append({
                "id": row[0],
                "userId": row[1],
                "timestamp": row[2],
                "userTranscript": row[3],
                "userAudioUrl": row[4],
                "gptResponse": row[5],
                "gptAudioUrl": row[6],
            })

        return JSONResponse(content=logs)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        conn.close()
        return {"message": "Conversation log stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import csv
from fastapi.responses import StreamingResponse
from io import StringIO

@app.get("/logs.csv")
def download_logs_csv():
    try:
        conn = sqlite3.connect("logs.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conversation_logs")
        rows = cursor.fetchall()
        conn.close()

        output = StringIO()
        writer = csv.writer(output)

        # Write CSV header
        writer.writerow([
            "id", "userId", "timestamp", 
            "userTranscript", "userAudioUrl", 
            "gptResponse", "gptAudioUrl"
        ])

        # Write data rows
        for row in rows:
            writer.writerow(row)

        output.seek(0)
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=conversation_logs.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
