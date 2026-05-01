from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi.encoders import jsonable_encoder

from app.models.user import UserModel, UserCreate, UserUpdate

class CRUDUser:
    collection_name = "users"

    async def create(self, db: AsyncIOMotorDatabase, user: UserCreate) -> UserModel:
        user_data = jsonable_encoder(user)
        new_user = await db[self.collection_name].insert_one(user_data)
        created_user = await db[self.collection_name].find_one({"_id": new_user.inserted_id})
        return UserModel(**created_user)

    async def get(self, db: AsyncIOMotorDatabase, id: str) -> Optional[UserModel]:
        if not ObjectId.is_valid(id):
            return None
        user = await db[self.collection_name].find_one({"_id": ObjectId(id)})
        if user:
            return UserModel(**user)
        return None

    async def get_multi(self, db: AsyncIOMotorDatabase, skip: int = 0, limit: int = 100) -> List[UserModel]:
        users = []
        cursor = db[self.collection_name].find().skip(skip).limit(limit)
        async for document in cursor:
            users.append(UserModel(**document))
        return users

    async def update(self, db: AsyncIOMotorDatabase, id: str, obj_in: UserUpdate) -> Optional[UserModel]:
        if not ObjectId.is_valid(id):
            return None
        update_data = {k: v for k, v in obj_in.model_dump(exclude_unset=True).items()}
        if len(update_data) >= 1:
            update_result = await db[self.collection_name].update_one(
                {"_id": ObjectId(id)}, {"$set": update_data}
            )
            if update_result.modified_count == 1:
                if (
                    updated_user := await db[self.collection_name].find_one({"_id": ObjectId(id)})
                ) is not None:
                    return UserModel(**updated_user)
        if (
            existing_user := await db[self.collection_name].find_one({"_id": ObjectId(id)})
        ) is not None:
            return UserModel(**existing_user)
        return None

    async def delete(self, db: AsyncIOMotorDatabase, id: str) -> bool:
        if not ObjectId.is_valid(id):
            return False
        delete_result = await db[self.collection_name].delete_one({"_id": ObjectId(id)})
        return delete_result.deleted_count == 1

user_crud = CRUDUser()
