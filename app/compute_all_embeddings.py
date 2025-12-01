# scripts/precompute_embeddings.py
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import SessionLocal
from app import models
from app.helpers.embedding import update_summary_embedding
from tqdm import tqdm

def main():
    db = SessionLocal()
    try:
        # Get all summaries
        summaries = db.query(models.summary.Summary).all()
        
        for summary in tqdm(summaries):
            try:
                update_summary_embedding(db, summary)
            except Exception as e:
                print(f"Error processing summary {summary.id}: {e}")
                db.rollback()
                continue
        
        print("Done precomputing embeddings.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
