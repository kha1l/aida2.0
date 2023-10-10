import pandas as pd
from io import BytesIO
from datetime import datetime
from database.postgres_async import AsyncDatabase
from loggs.logger import Log


async def read_file_audit(audit, unit_list, user, code, concept):
    db = AsyncDatabase()
    logger = Log('AUDIT')
    pool = await db.create_pool()
    try:
        file_io = BytesIO(audit)
        df = pd.read_excel(file_io)
        unit_name = df.iloc[0, 1]
        if unit_name in unit_list:
            uuid = unit_list[unit_name]
            df = pd.read_excel(file_io, skiprows=12, header=None)
            df = df[[1, 2, 12]].dropna()
            dt = (df.iloc[0, 2]).split(' ')
            await db.drop_items(pool, uuid)
            try:
                date_order = datetime.strptime(f'{dt[2]} {dt[3]}', '%d.%m.%Y %H:%M')
            except IndexError:
                date_order = datetime.now().replace(microsecond=0)
            for i, row in df.iterrows():
                if i > 0:
                    await db.add_stock_items(pool, uuid, unit_name, row[1], row[2], row[12], date_order,
                                             user, code, concept)
            await pool.close()
            return unit_name
        else:
            await pool.close()
            return ''
    except Exception as e:
        await pool.close()
        logger.error(f'ERROR add audit - {e}')
        return ''

