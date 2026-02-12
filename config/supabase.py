from supabase import create_client, Client
from config.setting import env

def get_supabase_client() -> Client:
    """
    Returns an authenticated Supabase client using the Service Role Key.
    This client bypasses RLS policies.
    """
    return create_client(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY)

supabase_client = get_supabase_client()

