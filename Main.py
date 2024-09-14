import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
import uvicorn
from Models.ListingDataModel import ListingDataModel
from Models.ListingScrapingModel import ListingScrapingModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = ['*','chrome-extension://edclgijkckipjdcjloklldklbmiakabb']

# Add the CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/ScrapeListing')
def scrape_listing(scraping_model: ListingScrapingModel):
    soup = BeautifulSoup(scraping_model.html, 'html.parser')
    listing_data = ListingDataModel.from_soup(soup, scraping_model.link)
    body = listing_data.model_dump()
    print(body)
    response = requests.post('http://165.73.253.139:8080/api/Land/SaveLand', json=body, verify=False)
    if response.status_code != 200:
        raise Exception(f'.net Api responded with {response.status_code}, {response.text}')
    return ''


uvicorn.run(app, port=8000)
