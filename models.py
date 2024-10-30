from pydantic import BaseModel

class QueryResponse(BaseModel):
    query: str
    answer: str
