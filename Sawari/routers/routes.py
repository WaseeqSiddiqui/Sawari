from fastapi import FastAPI,Response,HTTPException,status,Depends,APIRouter
from .. import models,schemas,Oauth2
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List,Optional

router=APIRouter(prefix="/routes",
                 tags=['Routes'])

@router.get("/",response_model=List[schemas.RouteResponse],dependencies=[Depends(Oauth2.get_current_user)])
def get_routes(db:Session=Depends(get_db),limit:Optional[int]=None,skip:int=0,search:Optional[str]=''):
    #    cursor.execute('SELECT * FROM "Routes"')
    #    routes=cursor.fetchall()
    routes=db.query(models.Routes).filter(models.Routes.destination.contains(search)).limit(limit).offset(skip).all()
    return routes


@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.RouteResponse,dependencies=[Depends(Oauth2.admin_access)])
def add_route(route:schemas.RouteCreate,db:Session=Depends(get_db)):
    # cursor.execute('INSERT INTO "Routes" (origin,destination,departure_time,arrival_time,departure_date) VALUES (%s,%s,%s,%s,%s) RETURNING *',
    #               (route.origin,route.destination,route.departure_time,route.arrival_time,route.departure_date))
    # route=cursor.fetchone()
    # conn.commit()
    new_route=models.Routes(**route.dict())
    db.add(new_route)
    db.commit()
    db.refresh(new_route)
    return new_route


@router.get("/{id}",response_model=schemas.RouteResponse,dependencies=[Depends(Oauth2.get_current_user)])
def get_one_route(id:int,db:Session=Depends(get_db)):
    # cursor.execute('SELECT * FROM "Routes" WHERE route_id=%s',(id,))
    # route=cursor.fetchone()
    route=db.query(models.Routes).filter(models.Routes.route_id==id).first()
    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"route with id {id} not found")
    return route
    


@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT,dependencies=[Depends(Oauth2.admin_access)])
def cancel_route(id:int,db:Session=Depends(get_db)):
    # cursor.execute('DELETE FROM "Routes" WHERE route_id=%s RETURNING *',(id,))
    # canceled_route=cursor.fetchone()
    # conn.commit()
    route_query=db.query(models.Routes).filter(models.Routes.route_id==id)

    if route_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"route with id {id} not found")
    route_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}",response_model=schemas.RouteResponse,dependencies=[Depends(Oauth2.admin_access)])
def modify_route_details(id:int,route:schemas.RouteCreate,db:Session=Depends(get_db)):
    # cursor.execute('UPDATE "Routes" SET origin=%s,destination=%s,departure_time=%s,arrival_time=%s,departure_date=%s WHERE route_id=%s RETURNING *',
    #               (route.origin,route.destination,route.departure_time,route.arrival_time,route.departure_date,id,))
    # updated_route_info=cursor.fetchone()
    # conn.commit()
    updated_route=db.query(models.Routes).filter(models.Routes.route_id==id)

    if updated_route.first() ==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"route with id {id} not found")
    updated_route.update(route.dict(),synchronize_session=False)
    db.commit()
    return updated_route.first()