from sqlalchemy.sql import select
from Db.postgres import engine, attachments_table



async def insert_attachment(video=None, file=None, image=None, audio=None):
    async with engine.begin() as conn:
        table = attachments_table
        insert_data = {
            'video': video,
            'file': file,
            'image': image,
            'audio': audio
        }
        insertStmt = table.insert().values(**insert_data)
        await conn.execute(insertStmt)
        await conn.commit()


async def get_filled_attachment_by_id(id: int):
    async with engine.connect() as conn:
        table = attachments_table
        select_stmt = select(table).where(table.c.id == id)

        result = await conn.execute(select_stmt)
        row = result.fetchone()

        if row:
            if row['video']:
                return row['video']
            elif row['file']:
                return row['file']
            elif row['image']:
                return row['image']
            elif row['audio']:
                return row['audio']
        return None
    