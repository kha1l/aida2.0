from utils.connection import post_api
from loggs.logger import Log
from database.postgres_async import AsyncDatabase
from datetime import datetime
from utils.sending import sending


async def work_birthday(request, chat, dt):
    logger = Log('BIRTHDAY')
    try:
        for member in request['members']:
            dt_day = datetime.strptime(member['dateOfBirth'], '%Y-%m-%d').date()
            if dt.month == dt_day.month and dt.day == dt_day.day:
                rest = member['unitName']
                staff = member['positionName']
                name = member['firstName']
                lastname = member['lastName']
                age = dt.year - dt_day.year
                message = f'\U0001F38A День рождения в {rest}\n' \
                          f'<b>{lastname} {name}</b> \U0001F381\n' \
                          f'{staff}, ' \
                          f'Возраст:  {age}\n'
                await sending(chat, message, logger)
    except TypeError:
        logger.error(f'Type ERROR birthday')
    except KeyError:
        logger.error(f'Key ERROR birthday')


async def send_birthday():
    logger = Log('BIRTHDAY')
    db = AsyncDatabase()
    pool = await db.create_pool()
    orders = await db.select_orders(pool, 'birthday')
    for order in orders:
        hour = datetime.now().hour - 3 + order['timezone']
        if hour == 9:
            dt = datetime.now().date()
            for i in range(0, len(order['uuid']), 29):
                batch = order['uuid'][i:i + 29]
                uuids = ','.join(batch)
                members = await post_api(f'https://api.dodois.io/dodopizza/{order["country"]}/staff/members',
                                         order["access"], units=uuids, statuses='Active')
                await work_birthday(members, order["chat_id"], dt)
                try:
                    cnt = members['totalCount']
                    take = 100
                    while take < cnt:
                        members = await post_api(f'https://api.dodois.io/dodopizza/{"country"}/staff/members',
                                                 order["access"], units=uuids, statuses='Active', take=100, skip=take)
                        take += 100
                        await work_birthday(members, order["chat_id"], dt)
                except KeyError:
                    logger.error(f'Key ERROR birthday - {order["id"]}')
    await pool.close()