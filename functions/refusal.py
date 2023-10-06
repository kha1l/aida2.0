from database.postgres_async import AsyncDatabase
from utils.connection import post_api
from utils.sending import Send
from loggs.logger import Log
from datetime import datetime, timedelta


async def send_refusal():
    db = AsyncDatabase()
    pool = await db.create_pool()
    send = Send(db=db)
    logger = Log('refusal')
    orders = await db.select_orders(pool, 'refusal')
    for order in orders:
        for i in range(0, len(order["uuid"]), 29):
            batch = order["uuid"][i:i + 29]
            uuids = ','.join(batch)
            minutes = order['timezone'] * 60 - 180
            created_before = (datetime.now().replace(minute=0, second=0, microsecond=0)) + timedelta(minutes=minutes)
            dt_end = datetime.strftime(created_before, '%Y-%m-%dT%H:%M:%S')
            created_after = created_before - timedelta(hours=1)
            dt_start = datetime.strftime(created_after, '%Y-%m-%dT%H:%M:%S')
            refusal = await post_api(f'https://api.dodois.io/{order["concept"]}/{order["country"]}/accounting/cancelled-sales',
                                     order["access"], units=uuids, _from=dt_start, to=dt_end, take=900)
            try:
                product_dict = {}
                for ref in refusal['cancelledSales']:
                    if ref['orderId'] not in product_dict:
                        product_dict[ref['orderId']] = [f'- {ref["productName"]}', ref['price'], ref['soldAt'],
                                                        ref['unitName']]
                    else:
                        values = product_dict[ref['orderId']]
                        if ref['price'] != 0:
                            values[0] += f'\n      - {ref["productName"]}'
                            values[1] += ref['price']
                            product_dict[ref['orderId']] = values
                for key, values in product_dict.items():
                    tm = values[2].split('T')[-1]
                    message = f'\U000026D4 <b>Отмененный заказ в {values[3]}</b>\n\n' \
                              f'Время заказа: {tm}\n' \
                              f'Продукты:\n      {values[0]}\n' \
                              f'Стоимость: {int(values[1])} \U0001F4B5\n'
                    await send.sending(order["chat_id"], message, logger, order['id'])
            except TypeError:
                logger.error(f'ERROR refusal')
            except KeyError:
                logger.error(f'ERROR refusal')
    await pool.close()
