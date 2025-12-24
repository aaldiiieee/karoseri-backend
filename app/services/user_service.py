from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.users import User
from ..schemas.user import UserCreate, UserUpdate
import logging

logger = logging.getLogger("app")

class UserService:
    async def create_user(self, db: AsyncSession, user_in: UserCreate) -> User:
        logger.info("Creating user: %s", user_in)
        user = User(
            username=user_in.username,
            password=user_in.password, # TODO: Password should be hashed in real application
            role=user_in.role,
            is_active=user_in.is_active
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info("User created: %s", user)
        return user

    async def get_user(self, db: AsyncSession, user_id: UUID) -> Optional[User]:
        logger.info("Getting user: %s", user_id)
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_users(self, db: AsyncSession) -> List[User]:
        logger.info("Getting users")
        result = await db.execute(select(User))
        return result.scalars().all()

    async def update_user(self, db: AsyncSession, user_id: UUID, user_in: UserUpdate) -> Optional[User]:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        
        if not user:
            return None
            
        update_data = user_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)
            
        await db.commit()
        await db.refresh(user)
        return user

    async def delete_user(self, db: AsyncSession, user_id: UUID) -> bool:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        
        if not user:
            return False
            
        await db.delete(user)
        await db.commit()
        return True

user_service = UserService()
