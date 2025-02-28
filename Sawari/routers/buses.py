from fastapi import FastAPI,Response,HTTPException,status,Depends,APIRouter
from .. import models,schemas,Oauth2
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List,Optional

router=APIRouter(prefix="/buses",
                 tags=['Buses'])


@router.get("/",response_model=List[schemas.BusResponse],dependencies=[Depends(Oauth2.admin_access)])
def get_buses(db:Session=Depends(get_db),limit:Optional[int]=None,skip:int=0,search:Optional[str]=''):
    # cursor.execute('SELECT * FROM "Buses"')
    # buses=cursor.fetchall()
    buses=db.query(models.Buses).filter(models.Buses.name.contains(search)).limit(limit).offset(skip).all()
    return buses

@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.BusResponse,dependencies=[Depends(Oauth2.admin_access)])
def add_buses(bus:schemas.BusCreate,db:Session=Depends(get_db)):
    # cursor.execute('INSERT INTO "Buses" (name,capacity,bus_type,"Available") VALUES(%s,%s,%s,%s)RETURNING *',
    #             (bus.name,bus.capacity,bus.bus_type,bus.Available))
    # New_bus=cursor.fetchone()
    # conn.commit()
    
    existing_bus=db.query(models.Buses).filter(models.Buses.name==bus.name).first()
    if existing_bus:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Bus with this name already exists")
    
    route=db.query(models.Routes).filter(models.Routes.route_id==bus.route_id).first()
    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Route not found")

    new_bus=models.Buses(**bus.dict())
    db.add(new_bus)
    db.commit()
    db.refresh(new_bus)
    return new_bus


@router.get("/{id}",response_model=schemas.BusResponse,dependencies=[Depends(Oauth2.admin_access)])
def get_one_Bus(id:int,db:Session=Depends(get_db)):
    # cursor.execute('SELECT * FROM "Buses" WHERE bus_id=%s',((id,)))
    # bus=cursor.fetchone()
    bus=db.query(models.Buses).filter(models.Buses.bus_no==id).first()
    if not bus:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Bus with id {id} not found")
    return bus


@router.delete("/{id}",dependencies=[Depends(Oauth2.admin_access)])
def remove_bus(id:int,db:Session=Depends(get_db)):
    # cursor.execute('DELETE FROM "Buses" WHERE bus_id=%s RETURNING *',(id,))
    # removed_bus=cursor.fetchone()
    # conn.commit()
    bus=db.query(models.Buses).filter(models.Buses.bus_no==id)

    if  bus.first()== None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"bus with id {id} not found")
    bus.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}",response_model=schemas.BusResponse,dependencies=[Depends(Oauth2.admin_access)])
def modify_bus_details(id:int,bus:schemas.BusCreate,db:Session=Depends(get_db)):
    # cursor.execute('UPDATE "Buses" SET name=%s,capacity=%s,bus_type=%s,"Available"=%s WHERE bus_id=%s RETURNING *',
    #               (bus.name,bus.capacity,bus.bus_type,bus.Available,id,))
    # updated_bus_det=cursor.fetchone()
    # conn.commit()
    updated_bus=db.query(models.Buses).filter(models.Buses.bus_no==id)

    if updated_bus.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"bus with id {id} not found")
    updated_bus.update(bus.dict(),synchronize_session=False)
    db.commit()
    return updated_bus.first()
