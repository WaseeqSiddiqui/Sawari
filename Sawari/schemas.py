from pydantic import BaseModel,EmailStr
from typing import Literal
from datetime import time
from datetime import date

class User_Base(BaseModel):
    name:str
    email:EmailStr
    password:str
    role:str


class UserCreate(User_Base):
    pass


class UserResponse(BaseModel):
    user_id:int
    name:str
    email:EmailStr
    role:Literal["user","admin"]

    class Config:
        from_attributes=True



class Bus_Base(BaseModel):
    name:str
    capacity:int
    bus_type:Literal['AC','Non-AC']
    Available:bool
    route_id:int


class Route_Base(BaseModel):
    origin:str
    destination:str
    departure_time:time
    arrival_time:time
    departure_date:date

class Booking_Base(BaseModel):
    seats_booked:int
    gender:Literal['M','F']
    route_id:int
    

class BusCreate(Bus_Base):
    pass


class RouteCreate(Route_Base):
    pass


class BookingCreate(Booking_Base):
    pass

class RouteResponse(Route_Base):
    route_id:int

    class Config:
        from_attributes=True


class BusResponse(Bus_Base):
    bus_no:int
    route:RouteResponse

    class Config:
        from_attributes=True



class BookingResponse(Booking_Base):
    booking_no:int
    route:RouteResponse
    user:UserResponse


    class Config:
        from_attributes=True

    
class Login(BaseModel):
    username:EmailStr
    password:str

class Token(BaseModel):
    access_token:str
    token_type:str