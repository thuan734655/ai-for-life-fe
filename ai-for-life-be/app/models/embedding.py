from sqlalchemy import Column, Integer, ForeignKey, Text, UniqueConstraint
from app.db.base import Base

class JobEmbedding(Base):
    __tablename__ = "job_embedding"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_table.id"), nullable=False, unique=True, index=True)
    embedding = Column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint("job_id", name="uq_job_embedding_job_id"),
    )
