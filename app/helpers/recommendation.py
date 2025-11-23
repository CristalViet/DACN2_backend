# app/recommendation.py
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple
from sqlalchemy.orm import Session
from app import models

def _load_embeddings_from_db(db: Session) -> Tuple[List[int], np.ndarray]:
    """
    Returns (ids_list, vectors_np) for all summaries that have embeddings.
    """
    rows = db.query(models.summary.Summary.id, models.summary.Summary.embedding).filter(models.summary.Summary.embedding.isnot(None), models.summary.Summary.status == "approved").all()
    ids = []
    vectors = []
    for r in rows:
        sid, emb = r
        try:
            if isinstance(emb, str):
                vec = json.loads(emb)
            else:
                vec = emb  # JSON column might already be list
            ids.append(sid)
            vectors.append(vec)
        except Exception:
            continue
    if not vectors:
        return [], np.zeros((0, ))
    vectors_np = np.array(vectors, dtype=np.float32)
    return ids, vectors_np

def _compute_user_vector(db: Session, user_id: int) -> np.ndarray:
    """
    Average embeddings of the summaries the user favourited.
    """
    favourites = db.query(models.favourite.Favourite.summary_id).filter(models.favourite.Favourite.user_id == user_id).all()
    fav_ids = [f[0] for f in favourites]
    if not fav_ids:
        return None
    rows = db.query(models.summary.Summary.embedding).filter(models.summary.Summary.id.in_(fav_ids), models.summary.Summary.embedding.isnot(None)).all()
    vecs = []
    for (emb,) in rows:
        try:
            if isinstance(emb, str):
                vec = json.loads(emb)
            else:
                vec = emb
            vecs.append(vec)
        except Exception:
            continue
    if not vecs:
        return None
    return np.mean(np.array(vecs, dtype=np.float32), axis=0).reshape(1, -1)

def recommend_by_history(db: Session, user_id: int, top_k: int = 10, exclude_favourites: bool = True):
    """
    Returns list of summary ids sorted by similarity to user's avg vector.
    """
    user_vec = _compute_user_vector(db, user_id)
    if user_vec is None:
        return []  # No favourites or no embeddings

    ids, vectors = _load_embeddings_from_db(db)
    if vectors.size == 0:
        return []

    # Normalize vectors (cosine similarity via dot product after normalization)
    def normalize(a):
        norms = np.linalg.norm(a, axis=1, keepdims=True)
        norms[norms == 0] = 1
        return a / norms

    user_vec_norm = normalize(user_vec)
    vectors_norm = normalize(vectors)

    sims = (vectors_norm @ user_vec_norm.T).squeeze()  # dot-products (cosine)
    top_idx = np.argsort(sims)[-top_k:][::-1]

    # Map back to ids
    recommended = []
    for idx in top_idx:
        recommended.append({"summary_id": ids[idx], "score": float(sims[idx])})
    # Optionally exclude already favourited
    if exclude_favourites:
        favs = set(fav[0] for fav in db.query(models.favourite.Favourite.summary_id).filter(models.favourite.Favourite.user_id == user_id).all())
        recommended = [r for r in recommended if r["summary_id"] not in favs]
        # if filtered out reduce list or fetch additional items as fallback (not implemented here)
    return recommended
