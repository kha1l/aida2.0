from loggs.logger import Log
from utils.connection import post_api
from datetime import datetime, timedelta
from utils.sending import Send
import pytz


async def order_certs(data, access, dt_start, dt_end, chat):
    logger = Log('CERTIFICATES')
    send = Send()
    certificates = await post_api(f'https://api.dodois.io/{data[4]}/{data[1]}/delivery/vouchers',
                                  access, units=data[2], _from=dt_start, to=dt_end, take=500)
    orders = await post_api(f'https://api.dodois.io/{data[4]}/{data[1]}/delivery/couriers-orders',
                            access, units=data[2], _from=dt_start, to=dt_end, take=990)
    cert_dict = {}
    dt = dt_start.split('T')[0]
    dt_for_message = datetime.strptime(dt, '%Y-%m-%d')
    dt_for_message = datetime.strftime(dt_for_message, '%d.%m')
    try:
        rest = ''
        message = f'\U0001F4D1 <b>Сертификаты за {dt_for_message}</b>\n\n'
        for cert in certificates['vouchers']:
            cert_dict[cert['orderId']] = cert['orderAcceptedAtLocal']
        for order in orders['couriersOrders']:
            if order['orderId'] in cert_dict:
                rest = order['unitName']
                courier = await post_api(f'https://api.dodois.io/{data[4]}/{data[1]}/staff/'
                                         f'members/{order["courierStaffId"]}', access)
                name = f"{courier['lastName']} {courier['firstName']}"
                number = order['orderNumber']
                order_time = cert_dict[order['orderId']].split('T')[1]
                order_ass = timedelta(seconds=order['orderAssemblyAvgTime'])
                trip = order['tripOrdersCount']
                delivery = order['handedOverToDeliveryAt'].split('.')[0]
                order_delivery = datetime.strptime(delivery, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=pytz.UTC)
                order_delivery = order_delivery + timedelta(hours=int(data[3]))
                predict = f'Да \U0001F534'
                if order['predictedDeliveryTime'] > order['deliveryTime']:
                    predict = f'Нет‚ \U0001F7E2'
                time_cooking = order_delivery - timedelta(seconds=order['heatedShelfTime'])
                message += f'\U0001F6B4 Курьер: {name}\n' \
                           f'Номер заказа: {number}\n' \
                           f'Время заказа: {order_time}\n' \
                           f'Время готовности заказа: {time_cooking.time()}\n' \
                           f'Время сборки заказа: {order_ass}\n' \
                           f'Начало поездки: {order_delivery.time()}\n' \
                           f'Поездка дольше прогноза: {predict}\n' \
                           f'Заказов в поездке: {trip}\n\n'
        message += f'\U0001F4F2 <b>Отчет сертификатов составлен по пиццерии {rest}</b>'
        await send.sending_function(message, chat, logger)
    except TypeError as e:
        logger.error(f'Type ERROR certificates - {certificates} - {e}')
    except KeyError as e:
        logger.error(f'Key ERROR certificates - {certificates} - {e}')
