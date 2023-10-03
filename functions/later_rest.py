from loggs.logger import Log
from utils.connection import post_api
from utils.sending import sending_function
from datetime import datetime, timedelta

async def order_later_rest(data, access, dt_start, dt_end, chat):
    logger = Log('LATER_REST')
    dict_source = {
        'CallCenter': 'РљРѕР»Р»-С†РµРЅС‚СЂ', 'Website': 'Р’СЌР±-СЃР°Р№С‚',
        'Dine-in': 'Р РµСЃС‚РѕСЂР°РЅ', 'MobileApp': 'РњРѕР±РёР»СЊРЅРѕРµ РїСЂРёР»РѕР¶РµРЅРёРµ'
    }
    handover = await post_api(f'https://api.dodois.io/dodopizza/{data[1]}/production/orders-handover-time',
                              access, units=data[2], _from=dt_start, to=dt_end)
    dt = dt_start.split('T')[0]
    dt_for_message = datetime.strptime(dt, '%Y-%m-%d')
    dt_for_message = datetime.strftime(dt_for_message, '%d.%m')
    try:
        message = f'\U000023F1 <b>РћРїРѕР·РґР°РЅРёСЏ РІ СЂРµСЃС‚РѕСЂР°РЅ Р·Р° {dt_for_message}</b>\n\n'
        rest = ''
        for over in handover['ordersHandoverTime']:
            if over['salesChannel'] == 'Dine-in':
                if rest == '':
                    rest = over['unitName']
                number = over['orderNumber']
                time_order = over['orderTrackingStartAt'].split('T')[1].split('.')[0]
                track = timedelta(seconds=over['trackingPendingTime'])
                cooking = timedelta(seconds=over['cookingTime'])
                source = dict_source[over['orderSource']]
                prod = int(number.split('-')[-1])
                meet = over['trackingPendingTime'] + over['cookingTime']
                if prod == 0:
                    if meet > 300:
                        message += f'РќРѕРјРµСЂ Р·Р°РєР°Р·Р°: {number}\n' \
                                   f'Р’СЂРµРјСЏ Р·Р°РєР°Р·Р°: {time_order}\n' \
                                   f'Р’СЂРµРјСЏ РЅР° С‚СЂРµРєРёРЅРіРµ: {track}\n' \
                                   f'Р’СЂРµРјСЏ РїСЂРёРіРѕС‚РѕРІР»РµРЅРёСЏ: {cooking}\n' \
                                   f'РСЃС‚РѕС‡РЅРёРє Р·Р°РєР°Р·Р°: {source}\n\n'
                if 0 < prod < 4:
                    if meet > 900:
                        message += f'РќРѕРјРµСЂ Р·Р°РєР°Р·Р°: {number}\n' \
                                   f'Р’СЂРµРјСЏ Р·Р°РєР°Р·Р°: {time_order}\n' \
                                   f'Р’СЂРµРјСЏ РЅР° С‚СЂРµРєРёРЅРіРµ: {track}\n' \
                                   f'Р’СЂРµРјСЏ РїСЂРёРіРѕС‚РѕРІР»РµРЅРёСЏ: {cooking}\n' \
                                   f'РСЃС‚РѕС‡РЅРёРє Р·Р°РєР°Р·Р°: {source}\n\n'
                if prod >= 4:
                    if meet > 1500:
                        message += f'РќРѕРјРµСЂ Р·Р°РєР°Р·Р°: {number}\n' \
                                   f'Р’СЂРµРјСЏ Р·Р°РєР°Р·Р°: {time_order}\n' \
                                   f'Р’СЂРµРјСЏ РЅР° С‚СЂРµРєРёРЅРіРµ: {track}\n' \
                                   f'Р’СЂРµРјСЏ РїСЂРёРіРѕС‚РѕРІР»РµРЅРёСЏ: {cooking}\n' \
                                   f'РСЃС‚РѕС‡РЅРёРє Р·Р°РєР°Р·Р°: {source}\n\n'
        message += f'\n\U0001F4F2 <b>РћС‚С‡РµС‚ РѕРїРѕР·РґР°РЅРёР№ РІ СЂРµСЃС‚РѕСЂР°РЅ СЃРѕСЃС‚Р°РІР»РµРЅ РїРѕ РїРёС†С†РµСЂРёРё {rest}</b>'
        await sending_function(message, chat, logger)
    except TypeError:
        logger.error(f'Type ERROR later - {handover}')
    except KeyError:
        logger.error(f'Key ERROR later - {handover}')
