from database.postgres_async import AsyncDatabase
from loggs.logger import Log
from utils.connection import post_api
from datetime import datetime, timedelta


async def application_stock():
    db = AsyncDatabase()
    logger = Log('APP_STOCK')
    pool = await db.create_pool()
    access_stock = await db.get_units_stock_user(pool)
    user_units = {}
    dt_list = []
    for stock in access_stock:
        if stock['date_order'] not in dt_list:
            dt_list.append(stock['date_order'])
        user = stock['user_id']
        dt = stock['date_order']
        if user in user_units:
            value = user_units.get(user)
            value[0].append(stock['uuid'])
            value[1].append(dt)
            user_units[user] = value
        else:
            user_units[user] = ([stock['uuid']], [dt], stock['concept'], stock['code'])
    for key, v in user_units.items():
        skip, skip_cons, skip_cons_avg, skip_transfers = 0, 0, 0, 0
        take, take_cons, take_cons_avg, take_transfers = 1000, 1000, 1000, 1000
        tokens = await db.get_tokens(pool, key)
        uuid = ','.join(v[0])
        concept = v[2]
        code = v[3]
        dt_start = datetime.strftime(max(v[1]), '%Y-%m-%dT%H:%M:%S')
        dt_now = datetime.now().replace(microsecond=0)
        dt_end_avg = dt_now.replace(hour=0, minute=0, second=0)
        dt_end_avg_str = datetime.strftime(dt_end_avg, '%Y-%m-%dT%H:%M:%S')
        dt_start_avg = datetime.strftime(dt_end_avg - timedelta(days=7), '%Y-%m-%dT%H:%M:%S')
        dt_end = datetime.strftime(dt_now, '%Y-%m-%dT%H:%M:%S')
        dict_items, avg_cons_items = {}, {}
        reach, reach_cons, reach_cons_avg, reach_transfers = True, True, True, True
        while reach:
            response = await post_api(f'https://api.dodois.io/{concept}/{code}/accounting/incoming-stock-items',
                                      tokens['access'], units=uuid, _from=dt_start, to=dt_end,
                                      skip=skip, take=take)
            skip += take
            try:
                for item in response['incomingStockItems']:
                    item_id = item['stockItemId']
                    unit = item['unitId']
                    if (item_id, unit) in dict_items:
                        value = dict_items[(item_id, unit)]
                        value += item['quantity']
                        dict_items[(item_id, unit)] = value
                    else:
                        dict_items[(item_id, unit)] = item['quantity']
                if response['isEndOfListReached']:
                    reach = False
            except Exception as e:
                reach = False
                logger.error(f'ERROR app_stock incoming - {e}')
        while reach_transfers:
            response = await post_api(f'https://api.dodois.io/{concept}/{code}/accounting/stock-transfers',
                                      tokens['access'], units=uuid, receivedFrom=dt_start, receivedTo=dt_end,
                                      skip=skip_transfers, take=take_transfers, statuses='Received')
            skip_transfers += take_transfers
            try:
                for item in response['transfers']:
                    item_id = item['stockItemId']
                    unit_destination = item['destinationUnitId']
                    unit_origin = item["originUnitId"]
                    if (item_id, unit_destination) in dict_items:
                        value = dict_items[(item_id, unit_destination)]
                        value += item['receivedQuantity']
                        dict_items[(item_id, unit_destination)] = value
                    else:
                        dict_items[(item_id, unit_destination)] = item['receivedQuantity']
                    if (item_id, unit_origin) in dict_items:
                        value = dict_items[(item_id, unit_origin)]
                        value -= item['shippedQuantity']
                        dict_items[(item_id, unit_origin)] = value
                    else:
                        dict_items[(item_id, unit_origin)] = -item['shippedQuantity']
                if response['isEndOfListReached']:
                    reach_transfers = False
            except Exception as e:
                reach_transfers = False
                logger.error(f'ERROR app_stock transfers - {e}')
        while reach_cons:
            response = await post_api(f'https://api.dodois.io/{concept}/{code}/accounting/stock-consumptions-by-period',
                                      tokens['access'], units=uuid, _from=dt_start, to=dt_end,
                                      skip=skip_cons, take=take_cons)
            skip_cons += take_cons
            try:
                for item in response['consumptions']:
                    key_dict = (item['stockItemId'], item['unitId'])
                    quantity = item['quantity']
                    try:
                        dict_items[key_dict] -= quantity
                    except KeyError:
                        dict_items[key_dict] = -quantity
                if response['isEndOfListReached']:
                    reach_cons = False
            except Exception as e:
                reach_cons = False
                logger.error(f'ERROR app_stock consumptions - {e}')
        while reach_cons_avg:
            response = await post_api(f'https://api.dodois.io/{concept}/{code}/accounting/stock-consumptions-by-period',
                                      tokens['access'], units=uuid, _from=dt_start_avg, to=dt_end_avg_str,
                                      skip=skip_cons_avg, take=take_cons_avg)
            skip_cons_avg += take_cons_avg
            try:
                for item in response['consumptions']:
                    key_dict = (item['stockItemId'], item['unitId'])
                    quantity = item['quantity']
                    if key_dict in avg_cons_items:
                        value = avg_cons_items.get(key_dict)
                        value += quantity
                        avg_cons_items[key_dict] = value
                    else:
                        avg_cons_items[key_dict] = quantity
                if response['isEndOfListReached']:
                    reach_cons_avg = False
            except Exception as e:
                reach_cons_avg = False
                logger.error(f'ERROR app_stock consumptions_average - {e}')
        for key_item, value_item in dict_items.items():
            cons = None
            average_cons = avg_cons_items.get(key_item)
            if average_cons:
                cons = round(average_cons / 7 * 2, 2)
            await db.update_items(pool, key_item, value_item, dt_now, cons)
    await pool.close()
