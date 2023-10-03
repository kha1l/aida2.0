from database.postgres_async import AsyncDatabase
from utils.connection import post_api, public_api
from datetime import timedelta, datetime
from loggs.logger import Log
from utils.sending import sending


async def change_revenue(today, week):
    try:
        perc = round((today * 100 / week) - 100)
    except ZeroDivisionError:
        perc = 0
    if perc >= 0:
        perc = f'+{perc}'
        message = f'{int(today)} <b>{perc}%</b> \U0001F53C'
    else:
        message = f'{int(today)} <b>{perc}%</b> \U0001F53B'
    return message


async def command_metrics(order, db, pool):
    logger = Log('metrics')
    minutes = order['timezone'] * 60 - 180
    created_before = (datetime.now().replace(minute=0, second=0, microsecond=0)) - timedelta(minutes=minutes)
    dt_end = datetime.strftime(created_before, '%Y-%m-%dT%H:%M:%S')
    created_after = created_before.replace(hour=0)
    dt_start = datetime.strftime(created_after, '%Y-%m-%dT%H:%M:%S')
    for i in range(0, len(order['uuid']), 29):
        batch = order['uuid'][i:i + 29]
        uuids = ','.join(batch)
        delivery_stat = await post_api(f'https://api.dodois.io/dodopizza/{order["country"]}/delivery/statistics/',
                                       order["access"], units=uuids, _from=dt_start, to=dt_end)
        product = await post_api(f'https://api.dodois.io/dodopizza/{order["country"]}/production/productivity',
                                 order["access"], units=uuids, _from=dt_start, to=dt_end)
        handover = await post_api(f'https://api.dodois.io/dodopizza/{order["country"]}'
                                  f'/production/orders-handover-statistics',
                                  order["access"], units=uuids, _from=dt_start, to=dt_end, salesChannels='DineIn')
        for unit in order["uuid"]:
            avg_delivery, shelf, time_rest, cooking = timedelta(0), timedelta(0), timedelta(0), timedelta(0)
            productivity, prod_hour, orders_hour, cert = 0, 0, 0, 0
            rest = await db.get_data_rest(pool, unit)
            link = f'https://publicapi.dodois.io/{order["country"]}/api/v1/' \
                   f'OperationalStatisticsForTodayAndWeekBefore/{rest["unit_id"]}'
            revenue = await public_api(link)
            today = revenue['today']
            week = revenue['weekBeforeToThisTime']
            revenue_today = today['revenue']
            revenue_week = week['revenue']
            try:
                for delivery in delivery_stat['unitsStatistics']:
                    if delivery['unitId'] == unit:
                        avg_delivery = timedelta(seconds=delivery['avgDeliveryOrderFulfillmentTime'])
                        cooking = timedelta(seconds=delivery['avgCookingTime'])
                        shelf = timedelta(seconds=delivery['avgHeatedShelfTime'])
                        cert = delivery['lateOrdersCount']
                        if cert != 0:
                            cert = f'{cert} \U00002753'
            except KeyError:
                logger.error(f'ERROR delivery')
            except TypeError:
                logger.error(f'Type ERROR delivery')
            try:
                for prod in product['productivityStatistics']:
                    if prod['unitId'] == unit:
                        productivity = prod['salesPerLaborHour']
                        prod_hour = prod['productsPerLaborHour']
                        orders_hour = prod['ordersPerCourierLabourHour']
            except KeyError:
                logger.error(f'ERROR productivity')
            except TypeError:
                logger.error(f'Type ERROR productivity')
            try:
                for hand in handover['ordersHandoverStatistics']:
                    if hand['unitId'] == unit:
                        time_rest = timedelta(seconds=(hand['avgTrackingPendingTime'] + hand['avgCookingTime']))
            except KeyError:
                logger.error(f'ERROR handover')
            except TypeError:
                logger.error(f'Type ERROR handover')
            rev = await change_revenue(revenue_today, revenue_week)
            message = f'\U0001F4CA <b>Ключевые метрики в заведении {rest["name"]}' \
                      f' по состоянию на {dt_end.split("T")[-1].split(":")[0]} часов</b>\n\n' \
                      f'Выручка: {rev}\n' \
                      f'Производительность: {int(productivity)}\n' \
                      f'Продуктов на чел/час: {str(prod_hour).replace(".", ",")}\n' \
                      f'Скорость доставки: {avg_delivery}\n' \
                      f'Время на полке: {shelf}\n' \
                      f'Заказов на курьера/час: {str(orders_hour).replace(".", ",")}\n' \
                      f'Сертификаты: {cert}\n' \
                      f'Время приготовления в ресторан: {time_rest}\n' \
                      f'Время приготовления на доставку: {cooking}\n'
            await sending(order["chat_id"], message, logger)


async def send_metrics():
    db = AsyncDatabase()
    pool = await db.create_pool()
    orders = await db.select_orders(pool, 'metrics')
    hours = [23, 14, 19]
    for order in orders:
        hour = datetime.now().hour - 3 + order['timezone']
        if hour in hours:
            await command_metrics(order, db, pool)
    await pool.close()