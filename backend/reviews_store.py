"""Shared review persistence helpers.

Provides a Supabase-backed store when credentials are configured, with a JSON
file fallback for local development and demos.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

_supabase = None


def _get_supabase():
    global _supabase
    if _supabase is not None:
        return _supabase
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_KEY", "").strip() or os.getenv("SUPABASE_ANON_KEY", "").strip()
    if not url or not key:
        return None
    try:
        from supabase import create_client
        _supabase = create_client(url, key)
        return _supabase
    except Exception:
        return None


def is_supabase_configured() -> bool:
    return _get_supabase() is not None



SHARED_REVIEWS_FILE = os.getenv("SHARED_REVIEWS_FILE", "shared_reviews.json")


def _load_file() -> Dict[str, List[Dict]]:
    if not os.path.exists(SHARED_REVIEWS_FILE):
        return {}
    try:
        with open(SHARED_REVIEWS_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_file(data: Dict[str, List[Dict]]) -> None:
    with open(SHARED_REVIEWS_FILE, "w") as f:
        json.dump(data, f, indent=2)



def _reviews_from_row(row: Dict) -> Dict[str, Any]:
    raw_date = row.get("created_at") or row.get("date") or ""
    if hasattr(raw_date, "isoformat"):
        raw_date = raw_date.isoformat()
    return {
        "user_name": row.get("user_name", ""),
        "rating": int(row.get("rating", 0)),
        "comment": row.get("comment", ""),
        "verified": bool(row.get("verified", True)),
        "date": str(raw_date),
    }


def _get_reviews_supabase(business_id: str) -> List[Dict]:
    sb = _get_supabase()
    if not sb:
        return []
    try:
        r = sb.table("reviews").select("*").eq("business_id", business_id).order("created_at", desc=False).execute()
        rows = r.data or []
        return [_reviews_from_row(row) for row in rows]
    except Exception:
        return []


def _add_review_supabase(business_id: str, user_name: str, rating: int, comment: str, verified: bool = True) -> Optional[Dict]:
    sb = _get_supabase()
    if not sb:
        return None
    try:
        row = {
            "business_id": business_id,
            "user_name": user_name,
            "rating": rating,
            "comment": comment,
            "verified": verified,
        }
        r = sb.table("reviews").insert(row).execute()
        data = r.data
        if data and len(data) > 0:
            return _reviews_from_row(data[0])
        return None
    except Exception:
        return None



def get_reviews(business_id: str) -> List[Dict]:
    if _get_supabase() is not None:
        return _get_reviews_supabase(business_id)
    data = _load_file()
    reviews = data.get(business_id, [])
    return reviews if isinstance(reviews, list) else []


def get_reviews_bulk(business_ids: List[str]) -> Dict[str, List[Dict]]:
    if _get_supabase() is not None:
        out = {}
        for bid in business_ids:
            out[bid] = _get_reviews_supabase(bid)
        return out
    data = _load_file()
    return {bid: (data.get(bid, []) if isinstance(data.get(bid), list) else []) for bid in business_ids}


def add_review(business_id: str, user_name: str, rating: int, comment: str, verified: bool = True) -> Dict:
    review = {
        "user_name": user_name,
        "rating": rating,
        "comment": comment,
        "verified": verified,
        "date": datetime.now().isoformat(),
    }
    if _get_supabase() is not None:
        created = _add_review_supabase(business_id, user_name, rating, comment, verified)
        if created:
            review["date"] = created.get("date", review["date"])
        return review
    data = _load_file()
    reviews = data.get(business_id, [])
    if not isinstance(reviews, list):
        reviews = []
    reviews.append(review)
    data[business_id] = reviews
    _save_file(data)
    return review
