from loggs.logger import Log
from utils.connection import post_api
from utils.sending import sending_function
from datetime import datetime


async def change_time(minute):
    if minute >= 60:
        h = minute // 60
        m = minute % 60
        tm = f'{h}С‡. {m}Рј.'
    else:
        tm = f'{minute} Рј.'
    return tm


async def order_later(data, access, dt_start, dt_end, chat):
    logger = Log('LATER')
    schedule = await post_api(f'https://api.dodois.io/dodopizza/{data[1]}/staff/schedules',
                              access, units=data[2], staffType='Courier',
                              beginFrom=dt_start, beginTo=dt_end, take=990)
    shifts = await post_api(f'https://api.dodois.io/dodopizza/{data[1]}/staff/shifts',
                            access, units=data[2], staffTypeName='Courier',
                            clockInFrom=dt_start, clockInTo=dt_end, take=990)
    dt = dt_start.split('T')[0]
    dt_for_message = datetime.strptime(dt, '%Y-%m-%d')
    dt_for_message = datetime.strftime(dt_for_message, '%d.%m')
    try:
        message = f'\U0000203C <b>РћРїРѕР·РґР°РЅРёСЏ/РЅРµРІС‹С…РѕРґС‹ Р·Р° {dt_for_message}</b>\n\n'
        rest = ''
        schedule_dict = {}
        for sch in schedule['schedules']:
            schedule_dict[sch['staffId']] = [sch['scheduledShiftStartAtLocal'], sch['scheduledShiftEndAtLocal']]
        for shift in shifts['shifts']:
            shift_id = shift['staffId']
            rest = shift['unitName']
            if shift_id in schedule_dict:
                start_shift = datetime.strptime(shift['clockInAtLocal'], '%Y-%m-%dT%H:%M:%S')
                end_shift = datetime.strptime(shift['clockOutAtLocal'], '%Y-%m-%dT%H:%M:%S')
                sch_time = schedule_dict.get(shift_id)
                start_sch = datetime.strptime(sch_time[0], '%Y-%m-%dT%H:%M:%S')
                end_sch = datetime.strptime(sch_time[1], '%Y-%m-%dT%H:%M:%S')
                if start_shift > start_sch:
                    delta_start = (start_shift - start_sch).seconds / 60
                    if delta_start > 10:
                        tm = await change_time(int(delta_start))
                        courier = await post_api(f'https://api.dodois.io/dodopizza/{data[1]}/staff/'
                                                 f'members/{shift_id}', access)
                        name = f"{courier['lastName']} {courier['firstName']}"
                        sex = courier['sex']
                        if sex == 'Male':
                            sex_word = 'РѕРїРѕР·РґР°Р»'
                        else:
                            sex_word = 'РѕРїРѕР·РґР°Р»Р°'
                        message += f'\U000023F0 {name} {sex_word} РЅР° {tm}\n'

                if end_shift < end_sch:
                    delta_end = (end_sch - end_shift).seconds / 60
                    if delta_end > 10:
                        tm = await change_time(int(delta_end))
                        courier = await post_api(f'https://api.dodois.io/dodopizza/{data[1]}/staff/'
                                                 f'members/{shift_id}', access)
                        name = f"{courier['lastName']} {courier['firstName']}"
                        sex = courier['sex']
                        if sex == 'Male':
                            sex_word = 'СѓС€РµР»'
                        else:
                            sex_word = 'СѓС€Р»Р°'
                        message += f'\U000023F3 {name} {sex_word} СЂР°РЅСЊС€Рµ РЅР° {tm}\n'
                try:
                    del schedule_dict[shift_id]
                except KeyError:
                    pass
            else:
                courier = await post_api(f'https://api.dodois.io/dodopizza/{data[1]}/staff/'
                                         f'members/{shift_id}', access)
                name = f"{courier['lastName']} {courier['firstName']}"
                sex = courier['sex']
                if sex == 'Male':
                    sex_word = 'РІС‹С€РµР»'
                else:
                    sex_word = 'РІС‹С€Р»Р°'
                message += f'\U00002753 {name} {sex_word} РЅР° СЂР°Р±РѕС‚Сѓ РЅРµ РІ СЃРІРѕСЋ СЃРјРµРЅСѓ\n'
        for key in schedule_dict:
            courier = await post_api(f'https://api.dodois.io/dodopizza/{data[1]}/staff/'
                                     f'members/{key}', access)
            name = f"{courier['lastName']} {courier['firstName']}"
            sex = courier['sex']
            if sex == 'Male':
                sex_word = 'РІС‹С€РµР»'
            else:
                sex_word = 'РІС‹С€Р»Р°'
            message += f'\U0001F6A8 {name} РЅРµ {sex_word} РЅР° СЂР°Р±РѕС‚Сѓ\n'
        message += f'\n\U0001F4F2 <b>РћС‚С‡РµС‚ РѕРїРѕР·РґР°РЅРёР№ СЃРѕСЃС‚Р°РІР»РµРЅ РїРѕ РїРёС†С†РµСЂРёРё {rest}</b>'
        await sending_function(message, chat, logger)
    except TypeError:
        logger.error(f'Type ERROR later - {schedule}')
    except KeyError:
        logger.error(f'Key ERROR later - {schedule}')
