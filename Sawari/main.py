from fastapi import FastAPI
from .database import engine
from . import models
from .routers import buses,routes,bookings,users,auth

models.Base.metadata.create_all(bind=engine)

sawari=FastAPI(title="Sawari",summary="This is a FastAPI bus management app that helps you manage routes, schedules, and bookings with secure authentication and role-based access control.")

sawari.include_router(buses.router)
sawari.include_router(routes.router)
sawari.include_router(bookings.router)
sawari.include_router(users.router)
sawari.include_router(auth.router)


@sawari.get("/")
def root():
    return {"message":"Hello world"}




