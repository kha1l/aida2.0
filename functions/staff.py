from utils.connection import post_api
from loggs.logger import Log
from database.postgres_async import AsyncDatabase
from utils.sending import sending
from datetime import datetime, timedelta


async def work_staff(request, order, dt):
    logger = Log('STAFF')
    try:
        for member in request['members']:
            dt_day = datetime.strptime(member['dateOfBirth'], '%Y-%m-%d').date()
            hired = datetime.strptime(member['hiredOn'], '%Y-%m-%d').date()
            user_id = member['userId']
            delta_holiday = dt_day - dt
            delta_hired = hired - dt
            if delta_holiday == timedelta(days=1):
                when = 'Завтра'
            else:
                when = 'Через 2 недели'
            if delta_holiday == timedelta(days=14) or delta_holiday == timedelta(days=1):
                age = dt.year - dt_day.year
                if age % 5 == 0:
                    rest = member['unitName']
                    staff = member['positionName']
                    name = member['firstName']
                    lastname = member['lastName']
                    message = f'\U0001F38A {when} юбилей в {rest}\n' \
                              f'<b>{lastname} {name}</b> \U0001F381\n' \
                              f'{staff}, ' \
                              f'Возраст:  {age}\n'
                    await sending(order['chat_id'], message, logger)
            if delta_hired == timedelta(days=1):
                when = 'Завтра'
            else:
                when = 'Через 2 недели'
            if delta_hired == timedelta(days=14) or delta_hired == timedelta(days=1):
                rest = member['unitName']
                staff = member['positionName']
                name = member['firstName']
                lastname = member['lastName']
                hire = dt.year - dt_day.year
                message = f'\U0001F38A {when} годовщина работы в {rest}\n' \
                          f'<b>{lastname} {name}</b> \U0001F381\n' \
                          f'{staff}, ' \
                          f'Стаж:  {hire}\n'
                await sending(order['chat_id'], message, logger)
            person = await post_api(f'https://api.dodois.io/dodopizza/{order["country"]}/staff/members{user_id}',
                                    order["access"])
            if person['isHealthPermitAvailable']:
                health = datetime.strptime(person['healthPermitExpiresOn'], '%Y-%m-%d').date()
                health_val = datetime.strptime(person['healthPermitValidUntil'], '%Y-%m-%d').date()
                delta_health = health - dt
                delta_health_val = health_val - dt
                if delta_health == timedelta(days=1):
                    when = 'Завтра'
                else:
                    when = 'Через 2 недели'
                if delta_health_val == timedelta(days=1):
                    when_val = 'Завтра'
                else:
                    when_val = 'Через 2 недели'
                if delta_health == timedelta(days=14) or delta_health == timedelta(days=1):
                    rest = member['unitName']
                    staff = member['positionName']
                    name = member['firstName']
                    lastname = member['lastName']
                    message = f'\U0001F38A {when} заканчивается действие медициского осмотра в ' \
                              f'медицинской книжке в {rest}\n' \
                              f'<b>{lastname} {name}</b> \U0001F381\n' \
                              f'{staff}'
                    await sending(order['chat_id'], message, logger)
                if delta_health_val == timedelta(days=14) or delta_health_val == timedelta(days=1):
                    rest = member['unitName']
                    staff = member['positionName']
                    name = member['firstName']
                    lastname = member['lastName']
                    message = f'\U0001F38A {when_val} заканчивается действие медицинской книжки в {rest}\n' \
                              f'<b>{lastname} {name}</b> \U0001F381\n' \
                              f'{staff}'
                    await sending(order['chat_id'], message, logger)
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
        if hour == 9:
            dt = datetime.now().date()
            for i in range(0, len(order['uuid']), 29):
                batch = order['uuid'][i:i + 29]
                uuids = ','.join(batch)
                members = await post_api(f'https://api.dodois.io/dodopizza/{order["country"]}/staff/members',
                                         order["access"], units=uuids, statuses='Active')
                await work_staff(members, order, dt)
                try:
                    cnt = members['totalCount']
                    take = 100
                    while take < cnt:
                        members = await post_api(f'https://api.dodois.io/dodopizza/{"country"}/staff/members',
                                                 order["access"], units=uuids, statuses='Active', take=100, skip=take)
                        take += 100
                        await work_staff(members, order, dt)
                except KeyError:
                    logger.error(f'Key ERROR staff - {order["id"]}')
    await pool.close()
