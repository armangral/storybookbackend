import secrets

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.api.api_v1.main import api_router
from app.core.config import settings


app = FastAPI(
    title=f"{settings.PROJECT_TITLE}",
    description=f"{settings.PROJECT_DESCRIPTION}",
    version=f"{settings.PROJECT_VERSION}",
    contact={
        "email": f"{settings.PROJECT_DEV_EMAIL}",
    },
    license_info={
        "name": f"{settings.PROJECT_LICENSE_INFO}",
    },
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(
        credentials.username, settings.DOCS_USERNAME
    )
    correct_password = secrets.compare_digest(
        credentials.password, settings.DOCS_PASSWORD
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/docs")
async def get_documentation(username: str = Depends(get_current_username)):  # noqa: ARG001
    return get_swagger_ui_html(
        openapi_url="/openapi.json", title=f"{settings.PROJECT_TITLE}"
    )


@app.get("/openapi.json")
async def openapi(username: str = Depends(get_current_username)):  # noqa: ARG001
    return get_openapi(
        title=f"{settings.PROJECT_TITLE}",
        description=f"{settings.PROJECT_DESCRIPTION}",
        version=f"{settings.PROJECT_VERSION}",
        contact={
            "email": f"{settings.PROJECT_DEV_EMAIL}",
        },
        license_info={
            "name": f"{settings.PROJECT_LICENSE_INFO}",
        },
        routes=app.routes,
    )


origins = [
    "http://localhost:5173",
    "http://192.168.0.100:5173",
    "http://192.168.0.103:5173",
    "http://192.168.0.108:5173",
    "https://192.168.118.133:5173",
    "https://192.168.72.133:5173",
    "https://192.168.206.133:5173"
    "http://localhost:3003",
    "http://49.12.34.250:3003",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return "Welcome to our System"


app.include_router(api_router, prefix="/api/v1")
