import uuid
from pydantic import BaseModel
from typing import Any, Optional


class PropertyBase(BaseModel):
    property_id: str
    property_url: Optional[str] = None
    sku: Optional[str] = None
    property_descr: Optional[str] = None
    feature_image: Optional[str] = None
    unit: Optional[str] = None
    street_address: Optional[str] = None
    area: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    region_code: Optional[str] = None
    country: Optional[str] = None
    property_status: Optional[str] = None
    house_price: Optional[str] = None
    rental_estimate: Optional[str] = None
    estimated_value: Optional[str] = None
    rental_yield: Optional[str] = None
    rental_dom: Optional[str] = None
    tax: Optional[str] = None
    tax_year: Optional[str] = None
    year_build: Optional[str] = None
    size: Optional[str] = None
    size_unit: Optional[str] = None
    lot_size: Optional[str] = None
    lot_size_unit: Optional[str] = None
    maintenance_fees: Optional[str] = None
    parking: Optional[str] = None
    bedrooms: Optional[str] = None
    bathrooms: Optional[str] = None
    garage: Optional[str] = None
    type_home: Optional[str] = None
    listing_date: Optional[Any] = None
    updated_on: Optional[str] = None

class PropertyCreate(PropertyBase):
    pass

class PropertyOut(PropertyBase):
    id: uuid.UUID
    class Config:
        orm_mode = True
