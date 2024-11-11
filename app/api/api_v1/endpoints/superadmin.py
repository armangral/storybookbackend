from uuid import UUID
import uuid
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_current_active_super_admin,

    get_session,
)

from app.core.wasabi import s3_download_file
from app.crud.chat_pdf import get_all_pdf_collections_count, get_all_pdfs, get_pdf_for_user
from app.crud.user import (
    create_user_with_admin,
    get_all_users,
    get_user_by_id,
    get_user_by_username,
)


from app.schemas.user import UserCreateWithAdmin, UserOut

router = APIRouter()




# Get all users
@router.get("/users", response_model=list[UserOut])
async def fetch_all_users(
    db: AsyncSession = Depends(get_session),
    admin=Depends(get_current_active_super_admin),
):
    users = await get_all_users(db)
    if not users:
        return []
    return users


@router.post("/users")
async def create_new_user(
    user_in: UserCreateWithAdmin,
    db: AsyncSession = Depends(get_session),
    admin=Depends(get_current_active_super_admin),
):
    user = await get_user_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    await create_user_with_admin(db, user_in)

    await db.commit()
    return {"msg": "User created successfully"}

# Set the status of user as active
@router.put("/users/{user_id}")
async def activate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_session),
    admin=Depends(get_current_active_super_admin),
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    await db.commit()
    return {"msg": "User activated successfully"}

# Set the status of user as inactive
@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_session),
    admin=Depends(get_current_active_super_admin),
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    await db.commit()
    return {"msg": "User deactivated successfully"}



# get all chat_pdfs for user
@router.get("/pdfs")
async def get_all_pdfs_for_user(
    admin=Depends(get_current_active_super_admin),
    db: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 10,
):
    # Fetch all PDF conversion records
    chat_pdfs = await get_all_pdfs(db,skip, limit)
    if not chat_pdfs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PDFs not found"
        )
    count = await get_all_pdf_collections_count(db)

    return {"data": chat_pdfs, "total_elements": count}


@router.get("{user_id}/pdfs/{pdf_id}/download")
async def download_pdf_related_to_user(
    pdf_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
):
    # Fetch the user by ID
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Fetch the PDF conversion record associated with the user
    chat_pdf = await get_pdf_for_user(db, user.id, pdf_id)
    if not chat_pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PDF not found"
        )

    print(chat_pdf.name_internal)

    # Download the PDF file from storage (Wasabi/S3/etc.)
    s3_response = await s3_download_file(chat_pdf, "chat_pdfs")

    # Return the PDF file as a response
    return Response(
        content=s3_response,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{chat_pdf.original_filename}"'
        },
    )