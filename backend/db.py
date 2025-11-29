import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client, Client

SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
supabase: Client = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

_inmemory_logs = []

def log_query(question=None, answer=None, sources=None, limit=50):
    # If this is only a "fetch logs" call:
    if question is None and answer is None and sources is None:
        return _inmemory_logs[:limit]

    entry = {
        'question': question or "",
        'answer': answer or "",
        'sources': ','.join(sources) if sources else ""
    }

    if supabase:
        try:
            supabase.table('kb_logs').insert(entry).execute()
        except Exception:
            _inmemory_logs.insert(0, entry)
    else:
        _inmemory_logs.insert(0, entry)

    return _inmemory_logs[:limit]
