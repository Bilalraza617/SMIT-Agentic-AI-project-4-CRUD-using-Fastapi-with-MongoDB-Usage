import asyncio
from app.db.mongodb import connect_to_mongo, get_database, close_mongo_connection
from app.crud.user import user_crud

async def main():
    try:
        await connect_to_mongo()
        db = get_database()
        users = await user_crud.get_multi(db, skip=0, limit=10)
        print("Users:", users)
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())
