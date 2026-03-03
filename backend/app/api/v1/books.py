from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.book import Book
from app.db.models.job import Job
from app.db.session import get_db
from app.workers.celery_app import celery_app

router = APIRouter(prefix="/books")


class CreateBookRequest(BaseModel):
    original_filename: str
    title: str | None = None


class CreateBookResponse(BaseModel):
    book_id: str
    job_id: str


@router.post("", response_model=CreateBookResponse)
async def create_book(payload: CreateBookRequest, db: AsyncSession = Depends(get_db)):
    book = Book(title=payload.title, original_filename=payload.original_filename)
    db.add(book)
    await db.flush()  # assigns book.id

    job = Job(book_id=book.id, status="QUEUED", progress=0)
    db.add(job)
    await db.commit()

    celery_app.send_task("ingest_book", args=[str(job.id)])

    return CreateBookResponse(book_id=str(book.id), job_id=str(job.id))


@router.get("/jobs/{job_id}")
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    # Job.id is UUID in DB; SQLAlchemy can compare with a UUID or a string
    stmt = select(Job).where(Job.id == job_id)
    res = await db.execute(stmt)
    job = res.scalar_one_or_none()
    if job is None:
        return {"error": "job_not_found"}

    return {
        "job_id": str(job.id),
        "status": job.status,
        "progress": job.progress,
        "error": job.error,
    }
