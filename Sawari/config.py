from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_name:str
    database_username:str
    database_password:str
    database_port:str
    database_hostname:str
    secret_key:str
    algorithm:str
    access_token_minutes:int

    class Config:
        env_file=".env"


settings=Settings()
