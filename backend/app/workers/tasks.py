import time
import uuid

import psycopg
from celery import shared_task

from app.core.config import get_settings

settings = get_settings()


def _sync_db_url() -> str:
    # Alembic & psycopg need the sync URL (no +asyncpg)
    return settings.database_url.replace("+asyncpg", "")


@shared_task(name="ingest_book")
def ingest_book(job_id: str) -> None:
    jid = uuid.UUID(job_id)

    with psycopg.connect(_sync_db_url()) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE jobs SET status=%s, progress=%s WHERE id=%s", ("RUNNING", 5, jid))
            conn.commit()

            time.sleep(1)

            cur.execute("UPDATE jobs SET progress=%s WHERE id=%s", (40, jid))
            conn.commit()

            time.sleep(1)

            cur.execute("UPDATE jobs SET progress=%s WHERE id=%s", (80, jid))
            conn.commit()

            time.sleep(1)

            cur.execute("UPDATE jobs SET status=%s, progress=%s WHERE id=%s", ("DONE", 100, jid))
            conn.commit()
