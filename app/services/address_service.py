from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.address import Address
from app.models.customer import Customer
from app.schemas.address import AddressCreate, AddressUpdate


def get_customer(db: Session, user_id: int):
    customer = (
        db.query(Customer)
        .filter(Customer.user_id == user_id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer profile not found"
        )

    return customer


def create_address(
    db: Session,
    user_id: int,
    address_data: AddressCreate
):
    customer = get_customer(db, user_id)

    if address_data.is_default:
        db.query(Address).filter(
            Address.customer_id == customer.customer_id,
            Address.is_default == True
        ).update({"is_default": False})

    address = Address(
        customer_id=customer.customer_id,
        full_name=address_data.full_name,
        phone=address_data.phone,
        address_line=address_data.address_line,
        city=address_data.city,
        state=address_data.state,
        pincode=address_data.pincode,
        is_default=address_data.is_default
    )

    db.add(address)
    db.commit()
    db.refresh(address)

    return address


def get_addresses(db: Session, user_id: int):
    customer = get_customer(db, user_id)

    return (
        db.query(Address)
        .filter(Address.customer_id == customer.customer_id)
        .all()
    )


def update_address(
    db: Session,
    user_id: int,
    address_id: int,
    address_data: AddressUpdate
):
    customer = get_customer(db, user_id)

    address = (
        db.query(Address)
        .filter(
            Address.address_id == address_id,
            Address.customer_id == customer.customer_id
        )
        .first()
    )

    if not address:
        raise HTTPException(
            status_code=404,
            detail="Address not found"
        )

    if address_data.is_default:
        db.query(Address).filter(
            Address.customer_id == customer.customer_id,
            Address.address_id != address_id,
            Address.is_default == True
        ).update({"is_default": False})

    address.full_name = address_data.full_name
    address.phone = address_data.phone
    address.address_line = address_data.address_line
    address.city = address_data.city
    address.state = address_data.state
    address.pincode = address_data.pincode
    address.is_default = address_data.is_default

    db.commit()
    db.refresh(address)

    return address


def delete_address(
    db: Session,
    user_id: int,
    address_id: int
):
    customer = get_customer(db, user_id)

    address = (
        db.query(Address)
        .filter(
            Address.address_id == address_id,
            Address.customer_id == customer.customer_id
        )
        .first()
    )

    if not address:
        raise HTTPException(
            status_code=404,
            detail="Address not found"
        )

    db.delete(address)
    db.commit()

    return {
        "message": "Address deleted successfully"
    }


def set_default_address(
    db: Session,
    user_id: int,
    address_id: int
):
    customer = get_customer(db, user_id)

    address = (
        db.query(Address)
        .filter(
            Address.address_id == address_id,
            Address.customer_id == customer.customer_id
        )
        .first()
    )

    if not address:
        raise HTTPException(
            status_code=404,
            detail="Address not found"
        )

    db.query(Address).filter(
        Address.customer_id == customer.customer_id
    ).update({"is_default": False})

    address.is_default = True

    db.commit()
    db.refresh(address)

    return address