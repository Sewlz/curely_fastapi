from fastapi import APIRouter

router = APIRouter()

@router.get("/test", summary="Test Authentication Route")
def test_auth():
    return {"message": "Auth module is working!"}
