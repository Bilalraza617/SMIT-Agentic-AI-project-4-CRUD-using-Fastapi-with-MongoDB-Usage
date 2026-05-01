from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.dependencies import get_db
from app.crud.user import user_crud
from app.models.user import UserModel, UserCreate, UserUpdate

router = APIRouter()

@router.post("/", response_description="Add new user", response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate = Body(...), db: AsyncIOMotorDatabase = Depends(get_db)):
    created_user = await user_crud.create(db, user)
    return created_user

@router.get("/", response_description="List all users", response_model=List[UserModel])
async def list_users(skip: int = 0, limit: int = 100, db: AsyncIOMotorDatabase = Depends(get_db)):
    users = await user_crud.get_multi(db, skip=skip, limit=limit)
    return users

@router.get("/{id}", response_description="Get a single user", response_model=UserModel)
async def get_user(id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = await user_crud.get(db, id)
    if user is not None:
        return user
    raise HTTPException(status_code=404, detail=f"User {id} not found")

@router.put("/{id}", response_description="Update a user", response_model=UserModel)
async def update_user(id: str, user: UserUpdate = Body(...), db: AsyncIOMotorDatabase = Depends(get_db)):
    updated_user = await user_crud.update(db, id, user)
    if updated_user is not None:
        return updated_user
    raise HTTPException(status_code=404, detail=f"User {id} not found")

@router.delete("/{id}", response_description="Delete a user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    deleted = await user_crud.delete(db, id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"User {id} not found")
