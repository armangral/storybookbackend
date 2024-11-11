from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings model.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    SQLALCHEMY_DATABASE_URI: str
    SQLALCHEMY_DATABASE_URI_TEST: str = ""

    PROJECT_TITLE: str
    PROJECT_DESCRIPTION: str
    PROJECT_VERSION: str
    PROJECT_DEV_EMAIL: str
    PROJECT_LICENSE_INFO: str

    DOCS_USERNAME: str
    DOCS_PASSWORD: str

    CRYPTO_JWT_SECRET: str
    CRYPTO_JWT_ALGO: str
    CRYPTO_JWT_ACESS_TIMEDELTA_MINUTES: int
    CRYPTO_JWT_REFRESH_TIMEDELTA_DAYS: int
    CRYPTO_JWT_DEFAULT_TIMEDELTA_MINUTES: int
    CRYPTO_API_ADMIN_KEY: str
    CRYPTO_API_ADMIN_KEY_NAME: str
    CRYTPTO_HMAC_ITIRATIONS: int
    CRYPTO_HASH_FUNCTION: str
    CRYPTO_PASSWD_ENCODING: str
    CRYPTO_MIN_PASSWD_LENGTH: int

    WASABI_API_BASE_URL: str
    WASABI_SECRET_KEY: str
    WASABI_ACCESS_KEY: str

    WASABI_BUCKET_NAME: str

    DELETE_FILE_WASABI_SECRET_KEY: str


settings = Settings()
