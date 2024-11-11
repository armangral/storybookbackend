from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import gen_new_key
from app.models.user import User
from app.schemas.user import UserCreate, UserCreateWithAdmin


async def get_all_users(db: AsyncSession):
    query = select(User).where(
        User.is_super_admin.is_(False) | User.is_super_admin.is_(None)
    )
    result = await db.execute(query)
    users = result.scalars().all()
    return users


# Get a user by ID
async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar()


# Get a user by username
async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar()


# Create a new user
async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    password_hash = gen_new_key(user_in.password)
    new_user = User(
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        username=user_in.username,
        password=password_hash[0],
        password_salt=password_hash[1],
        is_super_admin = False
    )

    db.add(new_user)
    await db.flush()  # This assigns an ID to the user

    return new_user



# Create a new user
async def create_user_with_admin(db: AsyncSession, user_in: UserCreateWithAdmin) -> User:
    password_hash = gen_new_key(user_in.password)
    new_user = User(
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        username=user_in.username,
        password=password_hash[0],
        password_salt=password_hash[1],
        is_super_admin=False,
    )

    db.add(new_user)
    await db.flush()  # This assigns an ID to the user

    return new_user


# Update user
async def update_user(db: AsyncSession, user_id: int, new_data: dict) -> User | None:
    user = await get_user_by_id(db, user_id)
    if user:
        for key, value in new_data.items():
            setattr(user, key, value)
        await db.commit()
        await db.refresh(user)
    return user


# Delete a user
async def delete_user(db: AsyncSession, user_id: int) -> None:
    user = await get_user_by_id(db, user_id)
    if user:
        await db.delete(user)
        await db.commit()




    

    