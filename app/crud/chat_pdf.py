import uuid
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_pdf import ChatPDFConversion



async def get_pdf_for_user(db: AsyncSession, user_id: uuid.UUID, chat_pdf_id: uuid.UUID):
    result = await db.execute(
        select(ChatPDFConversion).where(
            ChatPDFConversion.id == chat_pdf_id, ChatPDFConversion.created_by_user_id == user_id
        )
    )
    return result.scalars().first()


async def get_all_pdf_for_user(
    db: AsyncSession, user_id: uuid.UUID,skip:int,limit:int
):
    result = await db.execute(
        select(ChatPDFConversion)
        .where(
            ChatPDFConversion.created_by_user_id == user_id,
        )
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


# get count pdf collections for user
async def get_pdf_collections_count(db: AsyncSession,user_id:uuid.UUID):
    count = await db.execute(
        select(func.count())
        .select_from(ChatPDFConversion)
        .where(
            ChatPDFConversion.created_by_user_id == user_id,
        )
    )
    return count.scalars().first()


async def get_all_pdfs(db: AsyncSession,skip:int,limit:int):
    result = await db.execute(select(ChatPDFConversion).offset(skip).limit(limit))
    return result.scalars().all()


# get count all pdf collections
async def get_all_pdf_collections_count(db: AsyncSession):
    count = await db.execute(
        select(func.count())
        .select_from(ChatPDFConversion)
    )
    return count.scalars().first()