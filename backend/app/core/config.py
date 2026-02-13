from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "U-OIP API"
    database_url: str = "postgresql+psycopg://u_oip:u_oip@db:5432/u_oip"
    secret_key: str = "changeme"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
