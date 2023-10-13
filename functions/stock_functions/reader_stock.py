import pandas as pd
from io import BytesIO
from datetime import datetime
from database.postgres_async import AsyncDatabase
from loggs.logger import Log
import warnings


async def read_file_audit(audit, unit_list, user, code, concept):
    db = AsyncDatabase()
    logger = Log('AUDIT')
    pool = await db.create_pool()
    dt_now = datetime.now()
    try:
        file_io = BytesIO(audit)
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            df = pd.read_excel(file_io, engine="openpyxl", header=None)
        unit_name = df.iloc[1, 3]
        if unit_name in unit_list:
            uuid = unit_list[unit_name]
            dt = (df.iloc[2, 3]).split('-')[-1]
            tm = (df.iloc[4, 3]).split(' ')[-1]
            date_order = datetime.strptime(f'{dt} {tm}', '%d.%m.%Y %H:%M')
            df = df.dropna()
            await db.drop_items(pool, uuid)
            for i, row in df.iterrows():
                if row[0] != 'ID':
                    quantity = float(row[3].replace(',', '.'))
                    await db.add_stock_items(pool, uuid, unit_name, row[1], row[2], quantity, date_order,
                                             user, code, concept, row[0].lower(), dt_now)
            await pool.close()
            return unit_name
        else:
            await pool.close()
            return ''
    except Exception as e:
        await pool.close()
        logger.error(f'ERROR add audit - {e}')
        return ''

