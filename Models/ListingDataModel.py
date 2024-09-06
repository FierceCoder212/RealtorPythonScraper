import re
from typing import Optional

import zipcodes
from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel


class ListingDataModel(BaseModel):
    Price: Optional[int]
    Bedrooms: Optional[int]
    Bathrooms: Optional[int]
    Area: Optional[float]
    Acre: Optional[float]
    Address: Optional[str]
    Status: Optional[str]
    TimeOnWebsite: Optional[str]
    County: Optional[str]
    PricePerAcre: Optional[float]
    Link: Optional[str]
    Origin: Optional[str]

    @classmethod
    def from_soup(cls, soup: BeautifulSoup, link: str):
        price = cls.extract_data(soup, 'div[class^=Pricestyles__StyledPrice]', int, ['$', ','])
        beds = cls.extract_data(soup, 'li[data-testid=property-meta-beds] span[data-testid=meta-value]', int, [','])
        baths = cls.extract_data(soup, 'li[data-testid=property-meta-baths] span[data-testid=meta-value]', int, [','])
        sq_ft = cls.extract_data(soup, 'li[data-testid=property-meta-sqft] span[data-testid=meta-value]', float, [','])
        acres = cls.extract_data(soup, 'li[data-testid=property-meta-lot-size] span[data-testid=meta-value]', float, [','])
        address = cls.extract_data(soup, 'div[data-testid=address-line-ldp] h1', str)
        property_type = cls.extract_data(soup, 'ul[data-testid=key-facts] li svg[data-testid=icon-home]+div p.listing-key-fact-item-value', str)
        time_on_website = cls.extract_data(soup, 'ul[data-testid=key-facts] li svg[data-testid=icon-calendar]+div p.listing-key-fact-item-value', str)
        county = cls.get_county(address)
        price_per_acre = acres / price if price else None
        return cls(
            Price=price if price is not None else 0.0,
            Bedrooms=beds if beds is not None else 0,
            Bathrooms=baths if baths is not None else 0,
            Area=sq_ft if sq_ft is not None else 0.0,
            Acre=acres if acres is not None else 0.0,
            Address=address,
            Status=property_type,
            TimeOnWebsite=time_on_website,
            County=county,
            PricePerAcre=price_per_acre if price_per_acre is not None else 0.0,
            Link=link,
            Origin='Realtor'
        )

    @staticmethod
    def extract_data(soup: Tag | BeautifulSoup, selector: str, data_type: type = str, replace_chars=None):
        try:
            element = soup.select_one(selector)
            if not element:
                return None
            text = element.text.strip()
            if replace_chars:
                for char in replace_chars:
                    text = text.replace(char, '')
            return data_type(text)
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def get_county(address):
        if address:
            if match := re.search(r'TX\s?(\d+)', address):
                if zip_code_lookup := zipcodes.matching(match.group(1)):
                    if county := zip_code_lookup[0]['county']:
                        return county.replace('County', '').strip()
        return None
