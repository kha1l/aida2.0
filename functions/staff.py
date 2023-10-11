from utils.connection import post_api
from loggs.logger import Log
from database.postgres_async import AsyncDatabase
from utils.sending import Send
from datetime import datetime, timedelta


async def work_staff(request, order, dt, db):
    logger = Log('STAFF')
    send = Send(db=db)
    try:
        for member in request['members']:
            holiday_day = datetime.strptime(member['dateOfBirth'], '%Y-%m-%d').date() - timedelta(days=1)
            hired_day = datetime.strptime(member['hiredOn'], '%Y-%m-%d').date() - timedelta(days=1)
            holiday_week = holiday_day - timedelta(days=13)
            hired_week = hired_day - timedelta(days=13)
            if dt.day == holiday_day.day and dt.month == holiday_day.month:
                when_holiday = '\U0000203C Завтра'
                age = dt.year - holiday_day.year
            elif dt.day == holiday_week.day and dt.month == holiday_week.month:
                when_holiday = '\U00002755 Через 2 недели'
                age = dt.year - holiday_week.year
            else:
                when_holiday = ''
                age = 1
            if when_holiday:
                if age % 5 == 0:
                    rest = member['unitName']
                    staff = member['positionName']
                    name = member['firstName']
                    lastname = member['lastName']
                    message = f'{when_holiday} юбилей в {rest}\n' \
                              f'<b>{lastname} {name}</b> \U0001F490\n' \
                              f'{staff}, ' \
                              f'Возраст:  {age}\n'
                    await send.sending(order['chat_id'], message, logger, order['id'])
            if dt.day == hired_day.day and dt.month == hired_day.month:
                when_hired = '\U0000203C Завтра'
                hire = dt.year - hired_day.year
            elif dt.day == hired_week.day and dt.month == hired_week.month:
                when_hired = '\U00002755 Через 2 недели'
                hire = dt.year - hired_week.year
            else:
                when_hired = ''
                hire = 1
            if when_hired and hire != 0:
                rest = member['unitName']
                staff = member['positionName']
                name = member['firstName']
                lastname = member['lastName']
                message = f'{when_hired} годовщина работы в {rest}\n' \
                          f'<b>{lastname} {name}</b> \U0001F4BC\n' \
                          f'{staff}, ' \
                          f'Стаж:  {hire}\n'
                await send.sending(order['chat_id'], message, logger, order['id'])
    except TypeError:
        logger.error(f'Type ERROR staff')
    except KeyError:
        logger.error(f'Key ERROR staff')


async def send_staff():
    logger = Log('STAFF')
    db = AsyncDatabase()
    pool = await db.create_pool()
    orders = await db.select_orders(pool, 'staff')
    for order in orders:
        hour = datetime.now().hour - 3 + order['timezone']
        if hour == 11:
            dt = datetime.now().date()
            for i in range(0, len(order['uuid']), 29):
                batch = order['uuid'][i:i + 29]
                uuids = ','.join(batch)
                members = await post_api(f'https://api.dodois.io/{order["concept"]}/{order["country"]}/staff/members',
                                         order["access"], units=uuids, statuses='Active')
                await work_staff(members, order, dt, db)
                try:
                    cnt = members['totalCount']
                    take = 100
                    while take < cnt:
                        members = await post_api(f'https://api.dodois.io/{order["concept"]}/{order["country"]}/staff/members',
                                                 order["access"], units=uuids, statuses='Active', take=100, skip=take)
                        take += 100
                        await work_staff(members, order, dt, db)
                except KeyError:
                    logger.error(f'Key ERROR staff - {order["id"]}')
    await pool.close()
