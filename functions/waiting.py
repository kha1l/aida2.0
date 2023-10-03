from loggs.logger import Log
from utils.connection import post_api
from utils.sending import sending_function
from datetime import datetime, timedelta
import pytz

async def order_wait(data, access, dt_start, dt_end, chat):
    logger = Log('WAITING')
    skip = 0
    take = 500
    reach = True
    dt = dt_start.split('T')[0]
    dt_for_message = datetime.strptime(dt, '%Y-%m-%d')
    dt_for_message = datetime.strftime(dt_for_message, '%d.%m')
    try:
        message = f'\U0001F4A4 <b> Ожидания за {dt_for_message}</b>\n\n'
        rest = ''
        while reach:
            orders = await post_api(f'https://api.dodois.io/dodopizza/{data[1]}/delivery/couriers-orders',
                                    access, units=data[2], _from=dt_start, to=dt_end, skip=skip, take=take)
            skip += take
            for order in orders['couriersOrders']:
                wait = order['orderAssemblyAvgTime']
                if wait > 300:
                    rest = order['unitName']
                    courier = await post_api(f'https://api.dodois.io/dodopizza/{data[1]}/staff/'
                                             f'members/{order["courierStaffId"]}', access)
                    name = f"{courier['lastName']} {courier['firstName']}"
                    number = order['orderNumber']
                    delivery = order['handedOverToDeliveryAt'].split('.')[0]
                    order_delivery = datetime.strptime(delivery, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=pytz.UTC)
                    order_delivery = order_delivery + timedelta(hours=data[3])
                    trip = order['tripOrdersCount']
                    time_cooking = order_delivery - timedelta(seconds=order['heatedShelfTime'])
                    message += f'\U000026F7 Курьер: {name}\n' \
                               f'Номер заказа: {number}\n' \
                               f'Время готовности заказа: {time_cooking.time()}\n' \
                               f'Время сборки заказа: {timedelta(seconds=wait)}\n' \
                               f'Начало поездки: {order_delivery.time()}\n' \
                               f'Заказов в поездке: {trip}\n\n'
            try:
                if orders['isEndOfListReached']:
                    reach = False
            except TypeError:
                break
        message += f'\U0001F4F2 <b>Отчет ожиданий составлен по пиццерии {rest}</b>'
        await sending_function(message, chat, logger)
    except TypeError:
        logger.error(f'Type ERROR waiting')
    except KeyError:
        logger.error(f'Key ERROR waiting')
