from pydantic import BaseModel, ConfigDict, HttpUrl


class UrlCreate(BaseModel):
    target_url: HttpUrl


class UrlInfo(BaseModel):
    target_url: HttpUrl
    secret_key: str
    is_active: bool
    clicks: int

    model_config = ConfigDict(from_attributes=True)
