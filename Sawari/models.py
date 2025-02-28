from .database import Base
from sqlalchemy import Column,Integer,String,Boolean,CheckConstraint,Time,Date,ForeignKey
from sqlalchemy.orm import relationship



class Routes(Base):
        __tablename__="Routes"
        route_id=Column(Integer,nullable=False,primary_key=True,autoincrement=True)
        origin=Column(String,nullable=False)
        destination=Column(String,nullable=False)
        departure_time=Column(Time,nullable=False)
        arrival_time=Column(Time,nullable=False)
        departure_date=Column(Date,nullable=False)


class Buses(Base):
    __tablename__='Buses'
    bus_no=Column(Integer,primary_key=True,autoincrement=True)
    name=Column(String,nullable=False,unique=True)
    capacity=Column(Integer,nullable=False)
    bus_type=Column(String,nullable=False)
    Available=Column(Boolean,nullable=False,server_default="true")
    route_id=Column(Integer,ForeignKey(Routes.route_id,ondelete="CASCADE"),nullable=False)

    route=relationship(Routes)

    __table_args__=(
        CheckConstraint("capacity BETWEEN 35 AND 40",name="capacity_check"),
        CheckConstraint("bus_type IN('AC','Non-AC')",name="bus_type_check")
    )


class Users(Base):
       __tablename__="Users"
       user_id=Column(Integer,primary_key=True,nullable=False,autoincrement=True)
       name=Column(String,nullable=False)
       email=Column(String,nullable=False,unique=True)
       password=Column(String,nullable=False,unique=True)
       role=Column(String,default="user")


    
class Bookings(Base):
        __tablename__="Bookings"
        booking_no=Column(Integer,primary_key=True,nullable=False,autoincrement=True)
        seats_booked=Column(Integer,nullable=False)
        gender=Column(String,nullable=False)
        user_id=Column(Integer,ForeignKey(Users.user_id,ondelete="CASCADE"),nullable=False)
        route_id=Column(Integer,ForeignKey(Routes.route_id,ondelete="CASCADE"),nullable=False)

        route=relationship(Routes)
        user=relationship(Users)

        __table_args__=(
            CheckConstraint("gender IN('M','F')",name="gender_check"),
        )
