from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String,  Date
from app.core.db import Base
from app.models.mixin import SharedMixin


class Property(Base,SharedMixin):
    __tablename__ = "properties"

    property_id: Mapped[str] = mapped_column(String, primary_key=True)
    property_url: Mapped[str] = mapped_column(String)
    sku: Mapped[str] = mapped_column(String)
    property_descr: Mapped[str] = mapped_column(String)
    feature_image: Mapped[str] = mapped_column(String)
    unit: Mapped[str] = mapped_column(String)
    street_address: Mapped[str] = mapped_column(String)
    area: Mapped[str] = mapped_column(String)
    city: Mapped[str] = mapped_column(String)
    postal_code: Mapped[str] = mapped_column(String)
    region_code: Mapped[str] = mapped_column(String)
    country: Mapped[str] = mapped_column(String)
    property_status: Mapped[str] = mapped_column(String)
    house_price: Mapped[str] = mapped_column(String)
    rental_estimate: Mapped[str] = mapped_column(String)
    estimated_value: Mapped[str] = mapped_column(String)
    rental_yield: Mapped[str] = mapped_column(String)
    rental_dom: Mapped[str] = mapped_column(String)
    tax: Mapped[str] = mapped_column(String)
    tax_year: Mapped[str] = mapped_column(String)
    year_build: Mapped[str] = mapped_column(String)
    size: Mapped[str] = mapped_column(String)
    size_unit: Mapped[str] = mapped_column(String)
    lot_size: Mapped[str] = mapped_column(String)
    lot_size_unit: Mapped[str] = mapped_column(String)
    maintenance_fees: Mapped[str] = mapped_column(String)
    parking: Mapped[str] = mapped_column(String)
    bedrooms: Mapped[str] = mapped_column(String)
    bathrooms: Mapped[str] = mapped_column(String)
    garage: Mapped[str] = mapped_column(String)
    type_home: Mapped[str] = mapped_column(String)
    listing_date: Mapped[Date] = mapped_column(Date)
    updated_on: Mapped[str] = mapped_column(String)