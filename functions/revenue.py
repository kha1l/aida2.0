from database.postgres_async import AsyncDatabase
from utils.connection import public_api
from datetime import datetime
from loggs.logger import Log
from utils.sending import sending


async def change_revenue(today, week):
    try:
        perc = round((today * 100 / week) - 100)
    except ZeroDivisionError:
        perc = 0
    formatted = '{:,}'.format(int(today)).replace(',', ' ')
    if perc > 0:
        perc = f'+<b>{perc}%</b>'
    elif perc == 0:
        perc = f'<b>{perc}%</b>'
    else:
        perc = f'<b>{perc}%</b> \U0001F53B'
    return formatted, perc


async def command_revenue(order, db, pool):
    logger = Log('revenue')
    dt = datetime.now()
    dt_for_message = datetime.strftime(dt, '%d.%m')
    total_today, total_week = 0, 0
    message = f'\U0001F4CA <b>Выручка по сети на {dt_for_message}:</b>\n'
    data = []
    for unit in order["uuid"]:
        rest = await db.get_data_rest(pool, unit)
        link = f'https://publicapi.dodois.io/{order["country"]}/api/v1/' \
               f'OperationalStatisticsForTodayAndWeekBefore/{rest["unit_id"]}'
        revenue = await public_api(link)
        today = revenue['today']
        week = revenue['weekBeforeToThisTime']
        revenue_today = today['revenue']
        revenue_week = week['revenue']
        total_week += revenue_week
        total_today += revenue_today
        rev, perc = await change_revenue(revenue_today, revenue_week)
        data.append((rest["name"], rev, f'{perc}'))
    total_rev, total_perc = await change_revenue(total_today, total_week)
    data.append((f'\n<b>Итого:</b>', total_rev, total_perc))
    max_name_length = max(len(item[0]) for item in data)
    for item in data:
        name, value, percentage = item
        message += "{:<{}} {} ({})".format(name, max_name_length, value, percentage) + '\n'
    await sending(order["chat_id"], message, logger)


async def send_revenue():
    db = AsyncDatabase()
    pool = await db.create_pool()
    orders = await db.select_orders(pool, 'revenue')
    hours = [23, 12]
    for order in orders:
        hour = datetime.now().hour - 3 + order['timezone']
        if hour in hours:
            await command_revenue(order, db, pool)
    await pool.close()
