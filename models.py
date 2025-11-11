from sqlmodel import SQLModel, Field
from pgvector.sqlalchemy import Vector
from typing import Optional, List

class MedicalAbstract(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pmid: str = Field(unique=True, index=True)  # PubMed ID
    title: str
    abstract: str
    publication_date: Optional[str] = Field(default=None)
    
    # The "embedding" or "vector" column.
    # The 'dim=384' MUST match the model we are using (all-MiniLM-L6-v2)
    embedding: List[float] = Field(sa_column=Vector(dim=384))
