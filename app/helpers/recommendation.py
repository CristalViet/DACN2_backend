import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple
from sqlalchemy.orm import Session
from app import models


# ------------------------------
# 1. Load item embeddings
# ------------------------------
def _load_embeddings_from_db(db: Session):
    rows = db.query(
        models.summary.Summary.id,
        models.summary.Summary.embedding
    ).filter(
        models.summary.Summary.embedding.isnot(None),
        models.summary.Summary.status == "approved"
    ).all()

    ids = []
    vectors = []

    for sid, emb in rows:
        try:
            vec = json.loads(emb) if isinstance(emb, str) else emb
            ids.append(sid)
            vectors.append(vec)
        except:
            continue

    if not vectors:
        return [], np.zeros((0, ))

    return ids, np.array(vectors, dtype=np.float32)


# ------------------------------
# 2. Compute user vector (avg embedding)
# ------------------------------
def _compute_user_vector(db: Session, user_id: int):
    fav_ids = [
        f[0] for f in db.query(models.favourite.Favourite.summary_id)
        .filter(models.favourite.Favourite.user_id == user_id)
        .all()
    ]

    if not fav_ids:
        return None, []

    rows = db.query(models.summary.Summary.embedding).filter(
        models.summary.Summary.id.in_(fav_ids),
        models.summary.Summary.embedding.isnot(None)
    ).all()

    vecs = []
    for (emb,) in rows:
        try:
            vecs.append(json.loads(emb) if isinstance(emb, str) else emb)
        except:
            continue

    if not vecs:
        return None, fav_ids

    user_vec = np.mean(np.array(vecs, dtype=np.float32), axis=0)
    return user_vec.reshape(1, -1), fav_ids


# ------------------------------
# 3. Recommend 
# ------------------------------
def recommend_by_history(db: Session, user_id: int, top_k: int = 10):
    # Load embeddings
    item_ids, item_vectors = _load_embeddings_from_db(db)
    if item_vectors.size == 0:
        return []

    # Load user vector
    user_vec, fav_ids = _compute_user_vector(db, user_id)
    if user_vec is None:
        return []

    # Compute cosine similarity
    sims = cosine_similarity(user_vec, item_vectors)[0]  # shape: (N,)

    # Remove all favourites (same as Kaggle: train set removed)
    index_map = {item_ids[i]: i for i in range(len(item_ids))}
    for fid in fav_ids:
        if fid in index_map:
            sims[index_map[fid]] = -1e9

    # Top-K sort
    top_idx = sims.argsort()[::-1][:top_k]

    results = []
    for idx in top_idx:
        results.append({
            "summary_id": item_ids[idx],
            "score": float(sims[idx])
        })

    return results
