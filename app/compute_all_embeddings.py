# scripts/precompute_embeddings.py
import os
import json
from sentence_transformers import SentenceTransformer
import mysql.connector
from mysql.connector import Error
from tqdm import tqdm

MODEL_NAME = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "dacn2_user"),
        password=os.getenv("DB_PASS", "StrongP@ssw0rd123"),
        database=os.getenv("DB_NAME", "dacn2_db"),
        autocommit=False
    )

def main():
    model = SentenceTransformer(MODEL_NAME)
    db = get_db_connection()
    cursor = db.cursor(buffered=True)

    cursor.execute("SELECT id, title, COALESCE((SELECT GROUP_CONCAT(content SEPARATOR ' ') FROM content_sections WHERE summary_id = summaries.id), '') as full_text FROM summaries")
    rows = cursor.fetchall()

    for row in tqdm(rows):
        summary_id = row[0]
        title = row[1] or ""
        text = row[2] or ""
        # Combine title + content for embedding
        doc_text = (title + "\n" + text).strip()
        if not doc_text:
            continue
        vec = model.encode(doc_text, show_progress_bar=False).tolist()
        vec_json = json.dumps(vec)
        try:
            cursor.execute("UPDATE summaries SET embedding = %s WHERE id = %s", (vec_json, summary_id))
        except Error as e:
            print("DB error:", e)
            db.rollback()
    db.commit()
    cursor.close()
    db.close()
    print("Done precomputing embeddings.")

if __name__ == "__main__":
    main()
