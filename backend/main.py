from fastapi import FastAPI, HTTPException, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
from datetime import datetime
from typing import List


app = FastAPI(title="Note App API", version="1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
db = None

def init_firebase():
    global db

    try:
        cred_path = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")

        if not os.path.exists(cred_path):
            raise RuntimeError("Missing serviceAccountKey.json")

        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

        db = firestore.client()
        print("✅ Firebase connected")

    except Exception as e:
        print(f"❌ Firebase init failed: {e}")
        db = None

init_firebase()

class NoteCreate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)

class NoteUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)

class NoteResponse(BaseModel):
    id: str
    user_id: str
    content: str
    created_at: str
async def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = authorization.split(" ")[1]

    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
def ensure_db():
    if not db:
        raise HTTPException(status_code=500, detail="Database not ready")
    return db


@app.get("/")
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend running"}

@app.get("/auth/me")
async def get_me(user: dict = Depends(verify_token)):
    return {
        "user_id": user.get("uid"),
        "email": user.get("email")
    }


@app.post("/notes", response_model=NoteResponse)
async def create_note(
    note: NoteCreate,
    user: dict = Depends(verify_token)
):
    db_conn = ensure_db()

    user_id = user.get("uid")
    doc_ref = db_conn.collection("notes").document()

    new_note = {
        "id": doc_ref.id,
        "user_id": user_id,
        "content": note.content,
        "created_at": datetime.utcnow().isoformat()
    }

    try:
        doc_ref.set(new_note)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

    return new_note

@app.get("/notes", response_model=List[NoteResponse])
async def get_notes(
    sort_order: str = Query("desc"),
    limit: int = Query(50, le=100),
    user: dict = Depends(verify_token)
):
    db_conn = ensure_db()

    user_id = user.get("uid")

    try:
        docs = db_conn.collection("notes") \
            .where("user_id", "==", user_id) \
            .stream()

        notes = [doc.to_dict() for doc in docs]

        reverse = sort_order.lower() != "asc"

        notes.sort(
            key=lambda x: x.get("created_at", ""),
            reverse=reverse
        )

        return notes[:limit]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fetch error: {str(e)}")


@app.put("/notes/{note_id}")
async def update_note(
    note_id: str,
    note_update: NoteUpdate,
    user: dict = Depends(verify_token)
):
    db_conn = ensure_db()

    user_id = user.get("uid")
    doc_ref = db_conn.collection("notes").document(note_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Note not found")

    data = doc.to_dict()

    if data.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        doc_ref.update({
            "content": note_update.content,
            "updated_at": datetime.utcnow().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update error: {str(e)}")

    return {"status": "success", "message": "Note updated"}


@app.delete("/notes/{note_id}")
async def delete_note(
    note_id: str,
    user: dict = Depends(verify_token)
):
    db_conn = ensure_db()

    user_id = user.get("uid")
    doc_ref = db_conn.collection("notes").document(note_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Note not found")

    if doc.to_dict().get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        doc_ref.delete()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete error: {str(e)}")

    return {"status": "success", "message": "Note deleted"}