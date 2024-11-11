from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.property import Property
from app.schemas.property import PropertyCreate
from typing import List


async def create_properties(db: AsyncSession, properties: List[PropertyCreate]):
    db_properties = [Property(**property.dict()) for property in properties]
    db.add_all(db_properties)  # No need for await here
    await db.commit()
    for db_property in db_properties:
        await db.refresh(db_property)
    return db_properties


# Get all properties
async def get_all_properties(db: AsyncSession, skip: int, limit: int):
    query = (
        select(Property)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


# get count properties
async def get_properties_count(db: AsyncSession):
    count = await db.execute(select(func.count()).select_from(Property))
    return count.scalars().first()


# Get a prperty by PropertyID
async def get_property_by_propertyid(db: AsyncSession, property_id: str) -> Property | None:
    result = await db.execute(
        select(Property)
        .where(Property.property_id == property_id)
    )
    return result.scalar()