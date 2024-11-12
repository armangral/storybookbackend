# import json
# from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
# from fastapi.params import Body
# from fastapi.templating import Jinja2Templates
# from pydantic import BaseModel
# from sqlalchemy.orm import Session
# from typing import Any, List
# import qrcode
# import io
# import base64
# from datetime import datetime
# import uuid
# from jinja2 import Environment, FileSystemLoader
# import httpx
# from app.core.config import settings
# from app.api.deps import get_current_user, get_session as get_db
# from app.models.chat_pdf import ChatPDFConversion, ChatPDFStatus
# from app.core.wasabi import save

# router = APIRouter()


# def generate_qr_code(wasabi_url: str) -> str:
#     qr = qrcode.QRCode(version=1, box_size=10, border=5)
#     qr.add_data(wasabi_url)
#     qr.make(fit=True)
#     img = qr.make_image(fill_color="black", back_color="white")

#     # Convert PIL image to base64
#     buffered = io.BytesIO()
#     img.save(buffered, format="PNG")

#     print("converted to qrcode")
#     return base64.b64encode(buffered.getvalue()).decode()

# # Define the model for chat data
# class ChatMessage(BaseModel):
#     id: int
#     date: str
#     time: str
#     sender: str
#     text: str


# templates = Jinja2Templates(directory="templates")


# @router.post("/convert-chat")
# async def convert_chat(
#     chat_data: Any = Body(...),
#     zip_file: UploadFile = File(...),
#     db: Session = Depends(get_db),
#     # current_user=Depends(get_current_user),
# ):
#     try:
#         # Generate unique identifiers
#         pdf_internal_name = f"chat_pdf_{uuid.uuid4()}"
#         zip_internal_name = f"chat_zip_{uuid.uuid4()}"

#         # Upload ZIP file to Wasabi
#         zip_key = f"chat_files/{zip_internal_name}"
#         await save(zip_file, settings.WASABI_BUCKET_NAME, zip_key)

#         print("***********")

#         print(chat_data)

#         chat_data = json.loads(chat_data)

#         print("chat_data now is ",chat_data)

#         # Process messages and generate QR codes for files
#         for message in chat_data:
#             print("message is ",message)
#             if "file attached" in message.get("text", ""):
#                 filename = message["text"].split("(")[0].strip()
#                 wasabi_url = f"{settings.WASABI_API_BASE_URL}/{settings.WASABI_BUCKET_NAME}/chat_files/{zip_internal_name}/{filename}"

#                 print("yes")
#                 message["qr_code"] = generate_qr_code(wasabi_url)


#         print("doneeeeeeeeeee")
#         # Render HTML template
#         env = Environment(loader=FileSystemLoader("app/templates"))  # Updated path
#         template = env.get_template("whatsapp_chat.html")
#         html_content = template.render(
#             messages=chat_data,
#             generated_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             total_messages=len(chat_data),
#         )

#         # Convert to PDF using Gotenberg in Docker
#         async with httpx.AsyncClient() as client:
#             response = await client.post(
#                 "http://162.55.215.126:3000/forms/chromium/convert/html",
#                 files={
#                     "files": (
#                         "index.html",
#                         html_content.encode("utf-8"),
#                         "text/html",
#                     )
#                 },
#             )

#         if response.status_code != 200:
#             raise HTTPException(status_code=500, detail="PDF conversion failed")

#         # Save PDF to Wasabi
#         pdf_key = f"chat_pdfs/{pdf_internal_name}.pdf"
#         pdf_file = UploadFile(
#             filename=f"{pdf_internal_name}.pdf", file=io.BytesIO(response.content)
#         )
#         await save(pdf_file, settings.WASABI_BUCKET_NAME, pdf_key)

#         # # Create database record
#         # new_conversion = ChatPDFConversion(
#         #     name_internal=pdf_internal_name,
#         #     original_filename=zip_file.filename,
#         #     pdf_filename=f"{pdf_internal_name}.pdf",
#         #     status=ChatPDFStatus.COMPLETED,
#         #     # created_by_user_id=current_user.id,
#         #     # created_by_user_type=current_user.user_type,
#         #     wasabi_key=pdf_key,
#         #     zip_wasabi_key=zip_key,
#         # )

#         # db.add(new_conversion)
#         # db.commit()
#         # db.refresh(new_conversion)

#         return {"status": "success", "pdf_id": "new_conversion.id", "wasabi_key": pdf_key}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



from enum import Enum
import json
from fastapi import APIRouter, Response, UploadFile, File, Depends, HTTPException
from fastapi.params import Body
from typing import Any
import qrcode
import io
import base64
from datetime import datetime
import uuid
from jinja2 import Environment, FileSystemLoader
import httpx
from zipfile import ZipFile
from PIL import Image
from app.core.config import settings
from app.api.deps import get_current_user, get_session as get_db
from app.core.wasabi import s3_download_file, save
from app.crud.chat_pdf import get_all_pdf_for_user, get_pdf_collections_count, get_pdf_for_user
from app.crud.user import get_user_by_id
from app.models.chat_pdf import ChatPDFConversion, ChatPDFStatus
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

router = APIRouter()


def generate_qr_code(wasabi_url: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(wasabi_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

class PDFStyleType(str, Enum):
    DEFAULT = "DEFAULT"
    MODERN = "MODERN"
    DARK_MODE = "DARK"
    NEWSPAPER_MODE = "NEWSPAPER"


@router.post("/convert-chat")
async def convert_chat(
    style: PDFStyleType,
    chat_data: Any = Body(...),
    zip_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        pdf_internal_name = f"chat_pdf_{uuid.uuid4()}"
        zip_internal_name = f"chat_zip_{uuid.uuid4()}"
        zip_key = f"chat_files/{zip_internal_name}"

        # Save the ZIP file to Wasabi
        await save(zip_file, settings.WASABI_BUCKET_NAME, zip_key)

        # Reset the file pointer to the beginning after the first read
        zip_file.file.seek(0)

        # Load chat data from JSON
        chat_data = json.loads(chat_data)

        # Process messages and generate QR codes or embed images based on file type
        with ZipFile(io.BytesIO(await zip_file.read()), "r") as archive:
            for message in chat_data:

                if "file attached" in message.get("text", "") or "pièce jointe" in message.get("text", ""):
                    # Extract filename based on the format of the attachment line
                    if "file attached" in message.get("text", ""):
                        filename = message["text"].split("(")[0].strip()
                    else:
                        # Handle French attachment line format
                        filename = message["text"].split(": ")[1].split(" >")[0].strip()


                # if "file attached" in message.get("text", ""):
                #     filename = message["text"].split("(")[0].strip()
                    file_ext = filename.split(".")[-1].lower()  # Get the file extension

                    if filename in archive.namelist():
                        with archive.open(filename) as file:
                            # Check if the file is an image based on its extension

                            print("file ext is ",file_ext)
                            if file_ext in ["png", "jpg", "jpeg"]:
                                try:
                                    img = Image.open(file)
                                    buffered = io.BytesIO()
                                    print("its okay now")
                                    if file_ext in ["jpg","jpeg"]:
                                        img.save(buffered, format="JPEG")
                                    else:
                                        img.save(buffered, format="PNG")
                                    # img.save(buffered, format=file_ext.upper())
                                    print("SAVING")
                                    base64_img = base64.b64encode(
                                        buffered.getvalue()
                                    ).decode()
                                    print("OKE")
                                    message["embedded_image"] = (
                                        f"data:image/{file_ext};base64,{base64_img}"
                                    )
                                    print("DONEE IMAGE")
                                except IOError:
                                    # Handle invalid image files
                                    wasabi_url = f"{settings.WASABI_API_BASE_URL}/{settings.WASABI_BUCKET_NAME}/chat_files/{zip_internal_name}/{filename}"
                                    message["qr_code"] = generate_qr_code(wasabi_url)
                            else:
                                # If not an image, generate QR code for file
                                wasabi_url = f"{settings.WASABI_API_BASE_URL}/{settings.WASABI_BUCKET_NAME}/chat_files/{zip_internal_name}/{filename}"
                                message["qr_code"] = generate_qr_code(wasabi_url)

        print("DONEEEEE")
        # Render HTML template
        env = Environment(loader=FileSystemLoader("app/templates"))
        if style == PDFStyleType.MODERN:
            template = env.get_template("whatsapp_chat_modern.html")
        elif style == PDFStyleType.DARK_MODE:
            template = env.get_template("whatsapp_chat_dark_theme.html")
        elif style == PDFStyleType.NEWSPAPER_MODE:
            template = env.get_template("whatsapp_chat_newspaper.html")
        else:
            template = env.get_template("whatsapp_chat.html")
        html_content = template.render(
            messages=chat_data,
            generated_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_messages=len(chat_data),
        )

        print("NOw also done")

        # Convert to PDF using Gotenberg in Docker
        async with httpx.AsyncClient(timeout=680.0) as client:
            response = await client.post(
                "http://162.55.215.126:3000/forms/chromium/convert/html",
                files={
                    "files": (
                        "index.html",
                        html_content.encode("utf-8"),
                        "text/html",
                    )
                },
            )

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="PDF conversion failed")

        pdf_key = f"chat_pdfs/{pdf_internal_name}.pdf"
        pdf_file = UploadFile(
            filename=f"{pdf_internal_name}.pdf", file=io.BytesIO(response.content)
        )
        await save(pdf_file, settings.WASABI_BUCKET_NAME, pdf_key)


        # Create database record
        new_conversion = ChatPDFConversion(
            name_internal=f"{pdf_internal_name}.pdf",
            original_filename=zip_file.filename,
            pdf_filename=f"{pdf_internal_name}.pdf",
            status=ChatPDFStatus.COMPLETED,
            created_by_user_id=user.id,
            created_by_user_type=user.user_type,
            wasabi_key=pdf_key,
            zip_wasabi_key=zip_key,
        )

        db.add(new_conversion)
        await db.commit()
        await db.refresh(new_conversion)

        return {
            "status": "success",
            "pdf_id": new_conversion.id,
            "wasabi_key": pdf_key,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# get all chat_pdfs for user
@router.get("/pdfs")
async def get_all_pdfs_for_user(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
):
    # Fetch the user by ID
    user = await get_user_by_id(db, user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Fetch all PDF conversion records associated with the user
    chat_pdfs = await get_all_pdf_for_user(db, user.id,skip,limit)
    if not chat_pdfs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PDFs not found"
        )
    count = await get_pdf_collections_count(db,user.id)
    

    return {"data":chat_pdfs,"total_elements": count}


@router.get("/pdfs/{pdf_id}/download")
async def download_pdf_related_to_user(
    pdf_id: uuid.UUID,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Fetch the user by ID
    user = await get_user_by_id(db, user.id)
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



