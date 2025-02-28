from fastapi import FastAPI, Response, HTTPException, status, Depends, APIRouter
from sqlalchemy import func
from .. import models, schemas, Oauth2
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List, Optional

router = APIRouter(prefix="/bookings", tags=['Bookings'])


@router.get("/", response_model=List[schemas.BookingResponse], dependencies=[Depends(Oauth2.admin_access)])
def get_bookings(db: Session = Depends(get_db), limit: Optional[int] = None, skip: int = 0):
    bookings = db.query(models.Bookings).limit(limit).offset(skip).all()
    return bookings


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.BookingResponse)
def add_booking(booking: schemas.BookingCreate,db: Session = Depends(get_db),current_user: int = Depends(Oauth2.get_current_user)):
    route = db.query(models.Routes).filter(models.Routes.route_id == booking.route_id).first()
    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route does not exist")
    
    bus = db.query(models.Buses).filter(models.Buses.route_id == booking.route_id).first()
    if not bus:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No bus assigned to this route")
    
    existing_booking=db.query(models.Bookings).filter(models.Bookings.user_id==current_user['user_id']).first()
    if existing_booking:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Booking already exists")

    total_seats_booked = (db.query(func.coalesce(func.sum(models.Bookings.seats_booked), 0)).filter(models.Bookings.route_id == booking.route_id).scalar())

    available_seats = bus.capacity - total_seats_booked

    if booking.seats_booked > available_seats:
        raise HTTPException(status_code=400,detail=f"Only {available_seats} seats are available")

    new_booking = models.Bookings(user_id=current_user["user_id"], **booking.dict())
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    total_seats_booked += booking.seats_booked

    if total_seats_booked >= bus.capacity:
        bus.Available = False
        db.commit()

    return new_booking


@router.get("/{id}", response_model=schemas.BookingResponse)
def get_one_booking(id: int, db: Session = Depends(get_db), current_user: int = Depends(Oauth2.get_current_user)):
    
    booking = db.query(models.Bookings).filter(models.Bookings.booking_no == id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking with id {id} not found")
    
    if booking.user_id != current_user['user_id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to perform requested action")

    return booking


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_booking(id: int, db: Session = Depends(get_db), current_user: int = Depends(Oauth2.get_current_user)):
    booking_query = db.query(models.Bookings).filter(models.Bookings.booking_no == id)
    booking = booking_query.first()
    
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking with id {id} not found")

    if booking.user_id != current_user['user_id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to perform requested action")

    bus = db.query(models.Buses).filter(models.Buses.route_id == booking.route_id).first()
    
    total_seats_booked = (db.query(func.coalesce(func.sum(models.Bookings.seats_booked), 0)).filter(models.Bookings.route_id == booking.route_id).scalar()) - booking.seats_booked  

    booking_query.delete(synchronize_session=False)
    db.commit()

    if total_seats_booked < bus.capacity:
        bus.Available = True
        db.commit()

    return {"message": f"Booking with id {id} has been cancelled"}


@router.put("/{id}", response_model=schemas.BookingResponse)
def modify_booking_details(id: int,booking: schemas.BookingCreate,db: Session = Depends(get_db),current_user: int = Depends(Oauth2.get_current_user)):
    booking_query = db.query(models.Bookings).filter(models.Bookings.booking_no == id)
    booking_det = booking_query.first()

    if booking_det is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking with id {id} not found")
    
    if booking_det.user_id != current_user['user_id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to perform requested action")

    bus = db.query(models.Buses).filter(models.Buses.route_id == booking.route_id).first()

    total_seats_booked = (db.query(func.coalesce(func.sum(models.Bookings.seats_booked), 0)).filter(models.Bookings.route_id == booking.route_id, models.Bookings.booking_no != id)
        .scalar())

    available_seats = bus.capacity - total_seats_booked

    if booking.seats_booked > available_seats:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Only {available_seats} seats are available for modification")

    booking_query.update(booking.dict(), synchronize_session=False)
    db.commit()

    total_seats_booked += booking.seats_booked

    if total_seats_booked >= bus.capacity:
        bus.Available = False
    else:
        bus.Available = True

    db.commit()

    return booking_query.first()
