from database.postgres_async import AsyncDatabase
from utils.sending import Send
from loggs.logger import Log

async def send_stock():
    db = AsyncDatabase()
    pool = await db.create_pool()
    send = Send(db=db)
    logger = Log('stock')
    orders = await db.select_orders(pool, 'stock')
    for order in orders:
        message = f'Данная функции находится на стадии разработки.'
        await send.sending(order["chat_id"], message, logger, order['id'])
    await pool.close()
