def get_next_event_id():
    if not supabase: return 1
    try:
        response = supabase.table('events').select('id').execute()
        if response and response.data:
            ids = [int(event['id']) for event in response.data]
            return max(ids) + 1
        return 1
    except:
        return 1

def safe_count(table_name):
    if not supabase: return 0
    try:
        result = supabase.table(table_name).select('*').execute()
        return len(result.data) if result and result.data else 0
    except:
        return 0
