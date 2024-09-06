from pydantic import BaseModel


class ListingScrapingModel(BaseModel):
    html: str
    link: str
