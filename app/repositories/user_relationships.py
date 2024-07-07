import app.state

async def fetch_follower_count_by_user_id(user_id: int) -> int:
    query = """\
        SELECT COUNT(*)
        FROM users_relationships
        WHERE user2 = :user_id
    """
    params = {"user_id": user_id}

    follower_count = await app.state.database.fetch_val(query, params)
    return follower_count
