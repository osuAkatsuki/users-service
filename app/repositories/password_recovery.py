import app.state


async def delete_many_by_user_id(user_id: int, /) -> None:
    query = """\
        DELETE FROM password_recovery
        WHERE user_id = :user_id
    """
    params = {"user_id": user_id}
    await app.state.database.execute(query, params)
