"""
Persistent reviews storage for Chrysalis Connect.

Supports two backends:
- Supabase (when SUPABASE_URL and SUPABASE_KEY are set) – for production (e.g. Render).
- JSON file (shared_reviews.json) – fallback for local dev and the shared-reviews API.

Use this module for:
- /api/shared-reviews and /api/shared-reviews/bulk (always use this store).
- Main app business detail and add_review when Supabase is configured (so reviews persist on Render).
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Optional Supabase client (only used when env is set)
_supabase = None


def _get_supabase():
    """Lazy-init Supabase client if env vars are set."""
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
    """Return True if Supabase is configured and usable (for choosing main-app review source)."""
    return _get_supabase() is not None


# ---------------------------------------------------------------------------
# File backend (shared_reviews.json)
# ---------------------------------------------------------------------------

SHARED_REVIEWS_FILE = os.getenv("SHARED_REVIEWS_FILE", "shared_reviews.json")


def _load_file() -> Dict[str, List[Dict]]:
    """Load shared reviews from JSON file."""
    if not os.path.exists(SHARED_REVIEWS_FILE):
        return {}
    try:
        with open(SHARED_REVIEWS_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_file(data: Dict[str, List[Dict]]) -> None:
    """Save shared reviews to JSON file."""
    with open(SHARED_REVIEWS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------
# Supabase backend
# ---------------------------------------------------------------------------

def _reviews_from_row(row: Dict) -> Dict[str, Any]:
    """Convert a Supabase row to our review dict shape."""
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
    """Fetch reviews for one business from Supabase."""
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
    """Insert one review into Supabase. Returns the created review dict or None."""
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


# ---------------------------------------------------------------------------
# Public API (Supabase if configured, else file)
# ---------------------------------------------------------------------------

def get_reviews(business_id: str) -> List[Dict]:
    """Get all reviews for a business. Uses Supabase if configured, else file."""
    if _get_supabase() is not None:
        return _get_reviews_supabase(business_id)
    data = _load_file()
    reviews = data.get(business_id, [])
    return reviews if isinstance(reviews, list) else []


def get_reviews_bulk(business_ids: List[str]) -> Dict[str, List[Dict]]:
    """Get reviews for many business IDs. Returns { business_id: [reviews] }."""
    if _get_supabase() is not None:
        out = {}
        for bid in business_ids:
            out[bid] = _get_reviews_supabase(bid)
        return out
    data = _load_file()
    return {bid: (data.get(bid, []) if isinstance(data.get(bid), list) else []) for bid in business_ids}


def add_review(business_id: str, user_name: str, rating: int, comment: str, verified: bool = True) -> Dict:
    """
    Add a review. Uses Supabase if configured, else file.
    Returns the added review dict (with 'date' set).
    """
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
