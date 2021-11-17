from fastapi import APIRouter

router = APIRouter()

@router.get("/callback", status_code= 200)
def login():

    return {"msg":'Callback!'}