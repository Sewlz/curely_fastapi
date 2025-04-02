from fastapi import APIRouter, Depends, HTTPException
from app.modules.llm.schemas.llm_model import InputData, OutputData
from app.modules.llm.services.llm_service import TinyLlamaService

router = APIRouter()

model_service = TinyLlamaService()

@router.post("/generate", response_model=OutputData)
async def generate(input_data: InputData, service: TinyLlamaService = Depends(lambda: model_service)):
    try:
        response = service.generate_response(input_data.prompt)
        return OutputData(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")
