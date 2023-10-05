from loggs.logger import Log
from database.postgres_async import AsyncDatabase
from datetime import datetime, timedelta
from utils.sending import Send
from utils.connection import post_api, public_api


async def send_stationary():
    logger = Log('STATIONARY')
    db = AsyncDatabase()
    pool = await db.create_pool()
    send = Send(db=db)
    orders = await db.select_orders(pool, 'stationary')
    created_before = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    dt_end = datetime.strftime(created_before, '%Y-%m-%dT%H:%M:%S')
    created_after = created_before - timedelta(days=1)
    dt_start = datetime.strftime(created_after, '%Y-%m-%dT%H:%M:%S')
    for order in orders:
        hour = datetime.now().hour - 3 + order['timezone']
        if hour == 11:
            for unit in order['uuid']:
                handover = await post_api(f'https://api.dodois.io/dodopizza/{order["country"]}/production/orders-handover-time',
                                          order["access"], units=unit, _from=dt_start, to=dt_end)
                rest_id = await db.get_data_rest(pool, unit)
                link = f'https://publicapi.dodois.io/{order["country"]}/api/v1/unitinfo/{rest_id["unit_id"]}' \
                       f'/dailyrevenue/{created_after.year}/{created_after.month}/{created_after.day}'
                revenue = await public_api(link)
                try:
                    rest = revenue['UnitRevenue'][0]
                    revenue_rest = int(rest['StationaryRevenue'])
                    orders_rest = rest['StationaryCount']
                    mobile_rest = rest['StationaryMobileCount']
                    count_later, orders_dine = 0, 0
                    count_rest, time_rest = 0, 0
                    for over in handover['ordersHandoverTime']:
                        if over['salesChannel'] == 'Dine-in':
                            prod = int(over['orderNumber'].split('-')[-1])
                            meet = over['trackingPendingTime'] + over['cookingTime']
                            time_rest += meet
                            count_rest += 1
                            if prod == 0:
                                if meet > 300:
                                    count_later += 1
                            if 0 < prod < 4:
                                if meet > 900:
                                    count_later += 1
                            if prod >= 4:
                                if meet > 1500:
                                    count_later += 1
                        if over['orderSource'] == 'Dine-in':
                            orders_dine += 1
                    try:
                        perc_dine = int(round(orders_dine / orders_rest * 100, 0))
                    except ZeroDivisionError:
                        perc_dine = 0
                    try:
                        perc_mobile = int(round(mobile_rest / orders_rest * 100, 0))
                    except ZeroDivisionError:
                        perc_mobile = 0
                    try:
                        avg_meat = timedelta(seconds=round(time_rest / count_rest, 0))
                    except ZeroDivisionError:
                        avg_meat = timedelta(0)
                    message = f'\U0001F307 Краткий отчет по ресторану за {datetime.strftime(created_after, "%d.%m")}\n\n' \
                              f'\U0001F3C3 <b>{rest_id["name"]}</b>\n' \
                              f'Выручка: {revenue_rest}\n' \
                              f'Заказы: {orders_rest}\n' \
                              f'Среднее время приготовления: {avg_meat}\n' \
                              f'Опоздания: {count_later}\n\n' \
                              f'Заказов через приложение: {mobile_rest} ({perc_mobile}%)\n' \
                              f'Заказов на подносе: {orders_dine} ({perc_dine}%)\n\n'
                    await send.sending_statistics(order["chat_id"], message, order["country"], unit,
                                                  order['timezone'], logger, 'rest', order['id'])
                except TypeError:
                    logger.error(f'Type ERROR STATIONARY')
                except KeyError:
                    logger.error(f'Key ERROR STATIONARY')
                except IndexError:
                    logger.error(f'Index ERROR STATIONARY')
    await pool.close()
