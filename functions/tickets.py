from database.postgres_async import AsyncDatabase
from utils.connection import pyrus_auth, pyrus_api
from datetime import datetime, timezone, timedelta
from loggs.logger import Log
from utils.sending import Send
from configuration.conf import Config


async def send_tickets():
    cfg = Config()
    db = AsyncDatabase()
    pool = await db.create_pool()
    logger = Log('TICKETS')
    send = Send(db=db)
    token = await pyrus_auth()
    orders = await db.select_orders(pool, 'tickets')
    dict_catalog = {}
    dt = datetime.now(timezone.utc)
    dt_start = datetime.strftime(dt - timedelta(minutes=10), '%Y-%m-%dT%H:%M:%S')
    dt_end = datetime.strftime(dt, '%Y-%m-%dT%H:%M:%S')
    for country in cfg.catalogs:
        value = cfg.catalogs[country]
        catalogs = await pyrus_api(f'https://api.pyrus.com/v4/catalogs/{value["CatalogId"]}',
                                   token['access_token'])
        try:
            for catalog in catalogs['items']:
                if country == 'by' or country == 'uk':
                    dict_catalog[catalog['values'][1]] = catalog['item_id']
                else:
                    dict_catalog[catalog['values'][0]] = catalog['item_id']
        except KeyError:
            logger.error(f'ERROR for catalog in - {country}')
    for order in orders:
        data_catalog = []
        form_id = cfg.catalogs[order['country']]
        for uuid in order['uuid']:
            data_catalog.append(str(dict_catalog[uuid.upper()]))
        item_id = ','.join(data_catalog)
        data = {
            "field_ids": [1, 60, 57, 198, 13, 222, 37, 202, 196, 204, 203, 2, 261, 262, 134],
            "include_archived": "y",
            "created_after": dt_start + 'Z',
            "created_before": dt_end + 'Z',
            "fld198": item_id
        }
        pyrus = await pyrus_api(f'https://api.pyrus.com/v4/forms/{form_id["FormId"]}/register',
                                token['access_token'], data)
        try:
            tasks = pyrus['tasks']
        except KeyError:
            tasks = []
        for task in tasks:
            problem = []
            checker, comment, name = '', '', ''
            type_order, number_order, grade = '', 0, 0
            dt, tm = '', ''
            id_task = task['id']
            tickets = await pyrus_api(f'https://api.pyrus.com/v4/tasks/{id_task}', token['access_token'])
            try:
                ticket = tickets['task']
                fields = ticket['fields']
            except KeyError:
                logger.error('ERROR tickets/fields')
                fields = []
            for field in fields:
                if field['id'] == 198:
                    value = field['value']
                    try:
                        name = value['values'][1]
                    except IndexError:
                        name = ''
                    except ValueError:
                        name = ''
                elif field['id'] == 284:
                    try:
                        number_order = field['value']
                    except KeyError:
                        number_order = ''
                elif field['id'] == 285:
                    try:
                        dt = field['value']
                    except KeyError:
                        dt = ''
                elif field['id'] == 286:
                    try:
                        tm = field['value']
                    except KeyError:
                        tm = ''
                elif field['id'] == 280:
                    try:
                        value = field['value']
                        type_order = value['choice_names'][0]
                    except IndexError:
                        type_order = ''
                    except KeyError:
                        type_order = ''
                elif field['id'] == 13:
                    try:
                        value = field['value']['fields']
                    except KeyError:
                        value = []
                    for fld_value in value:
                        if fld_value['id'] == 142:
                            try:
                                grade = fld_value['value']
                            except KeyError:
                                grade = 0
                        elif fld_value['id'] == 143:
                            try:
                                comment = fld_value['value']
                            except KeyError:
                                comment = ''
                        elif fld_value['id'] == 144:
                            try:
                                checked = fld_value['value']['fields']
                            except KeyError:
                                checked = []
                            for check in checked:
                                if check['value'] == 'checked':
                                    checker = check['name']
                                else:
                                    checker = ''
                elif field['id'] == 202:
                    try:
                        values = field['value']
                    except KeyError:
                        values = []
                    for value in values:
                        cells = value['cells']
                        for cell in cells:
                            if cell['id'] == 203:
                                try:
                                    name_prob = cell['value']['values'][0]
                                    if name_prob in problem:
                                        pass
                                    else:
                                        problem.append(name_prob)
                                except KeyError:
                                    pass
                                except IndexError:
                                    pass
            if checker or comment or problem:
                try:
                    time_tz = (datetime.strptime(f'{dt} {tm}', '%Y-%m-%d %H:%M') +
                               timedelta(hours=order['timezone']))
                    dt_tz = datetime.strftime(time_tz, '%H:%M %d.%m.%Y')
                except ValueError:
                    dt_tz = ''
                prb = ', '.join(problem)
                message = f'\U0001F4AC Тикет от клиента\n\n' \
                          f'<b>Оценка: {grade}</b>\n' \
                          f'Заведение: {name}\n' \
                          f'Номер заказа: {number_order}\n' \
                          f'Тип заказа: {type_order}\n' \
                          f'Проблемы: {prb}\n' \
                          f'Комментарии: {comment}\n' \
                          f'Дата и время заказа: {dt_tz}\n'
                if prb == '':
                    message = message.replace('Проблемы: \n', '')
                if comment == '':
                    message = message.replace('Комментарии: \n', '')
                if dt_tz == '':
                    message = message.replace('Дата и время заказа: \n', '')
                await send.sending(order['chat_id'], message, logger, order['id'])
    await pool.close()
