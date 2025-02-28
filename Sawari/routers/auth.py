from fastapi import HTTPException,status,Depends,APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import database,utils,models,Oauth2,schemas
from sqlalchemy.orm import Session

router=APIRouter(
    prefix="/login",
    tags=["Authentication"]
)


@router.post("/",response_model=schemas.Token)
def login(credentials:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(database.get_db)):
    user=db.query(models.Users).filter(models.Users.email==credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid Cretdentials")
    
    if not utils.verify(credentials.password,user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Invalid Credentials")
    
    access_token=Oauth2.create_access_token(data={"user_id":user.user_id,"role":user.role})

    return {"access_token":access_token,"token_type":"bearer"}