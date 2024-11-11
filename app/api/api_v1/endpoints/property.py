import pandas as pd
from fastapi import APIRouter, UploadFile, HTTPException, Depends, status
from app.schemas.paging import Metadata, Page
from app.schemas.property import PropertyCreate, PropertyOut
from app.crud.property import create_properties, get_all_properties, get_properties_count, get_property_by_propertyid
from app.api.deps import get_current_active_super_admin, get_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()



def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Replace NaN values with empty strings or defaults where needed
    df.fillna(
        {
            "unit": "",
            "bedrooms": "0",
            "bathrooms": "0",
            "garage": "0",
            "parking": "0",
            "rental_dom": "0",
            "tax_year": "",
            "year_build": "",
            "house_price": "",
            "tax": "",
            "lot_size": "",

        },
        inplace=True,
    )

    # Convert date columns to datetime format, and set NaT for null values
    df["listing_date"] = pd.to_datetime(df["listing_date"], errors="coerce")

    # Convert all other fields to string format
    df = df.astype(
        {
            "property_url": "str",
            "property_id": "str",
            "sku": "str",
            "property_descr": "str",
            "feature_image": "str",
            "street_address": "str",
            "postal_code": "str",
            "region_code": "str",
            "property_status": "str",
            "size_unit": "str",
            "lot_size_unit": "str",
            "type_home": "str",
            "year_build": "str",
            "tax_year": "str",
            "rental_estimate": "str",
            "estimated_value": "str",
            "rental_yield": "str",
            "maintenance_fees":"str",
            "updated_on":"str",
            "rental_dom": "str",
            "parking":"str",
            "size":"str",
            "area":"str",
            "country":"str"
        }
    )

    return df


@router.post("/upload-properties")
async def upload_properties(file: UploadFile,
                            admin=Depends(get_current_active_super_admin), db: AsyncSession = Depends(get_session)):
    if file.content_type not in ["text/csv", "application/vnd.ms-excel"]:
        raise HTTPException(
            status_code=400, detail="Invalid file type. Please upload a CSV file."
        )

    # Read CSV file into DataFrame
    contents = await file.read()
    df = pd.read_csv(pd.io.common.BytesIO(contents))

    # Rename columns to match model fields
    df.rename(
        columns={
            "propertyUrl": "property_url",
            "propertyId": "property_id",
            "sku#": "sku",
            "propertyDescr": "property_descr",
            "featureImage": "feature_image",
            "streetAddress": "street_address",
            "postalCode": "postal_code",
            "regionCode": "region_code",
            "propertyStatus": "property_status",
            "housePrice": "house_price",
            "rentalEstimate": "rental_estimate",
            "estimatedValue": "estimated_value",
            "rentalYield": "rental_yield",
            "rentalDom": "rental_dom",
            "taxYear": "tax_year",
            "yearBuild": "year_build",
            "sizeUnit": "size_unit",
            "lotSize": "lot_size",
            "lotSizeUnit": "lot_size_unit",
            "maintenanceFees": "maintenance_fees",
            "typeHome": "type_home",
            "listingDate": "listing_date",
            "updatedOn": "updated_on",
            "size":"size",
            "area":"area",
            "country":"country"
        },
        inplace=True,
    )

    # Preprocess the DataFrame to match schema requirements
    df = preprocess_dataframe(df)

    # Convert DataFrame to list of PropertyCreate objects
    properties_data = df.to_dict(orient="records")
    properties = [PropertyCreate(**data) for data in properties_data]



    # Save to database
    await create_properties(db, properties)
    return {"message": "Properties uploaded successfully."}


# Admin - Get all properties
@router.get("/", response_model=Page[PropertyOut])
async def get_all_properties_info(
    db: AsyncSession = Depends(get_session),
    admin = Depends(get_current_active_super_admin),
    skip: int = 0,
    limit: int = 10,
):
    properties = await get_all_properties(db, skip, limit)
    count = await get_properties_count(db)
    return Page(data=properties, metadata=Metadata(total_elements=count))


# Admin - Get a specific property by PropertyID
@router.get("{property_id}", response_model=PropertyOut)
async def get_property_info_by_property_id(
    property_id: str,
    db: AsyncSession = Depends(get_session),
    admin=Depends(get_current_active_super_admin),
):
    property = await get_property_by_propertyid(db, property_id)
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Property not found"
        )
    return property
