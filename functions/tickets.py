from database.postgres_async import AsyncDatabase
from utils.connection import pyrus_auth, pyrus_api
from datetime import datetime, timezone, timedelta
from loggs.logger import Log
from utils.sending import Send
from configuration.conf import Config


class Ticket:
    problem = []
    checker, comment, name = '', '', ''
    type_order, number_order, grade = '', 0, 0
    dt, tm = '', ''


    async def get_ticket_all(self, fields):
        for field in fields:
            pass

    async def get_ticket_ru_kz(self, fields):
        for field in fields:
            if field['id'] == 198:
                value = field['value']
                try:
                    self.name = value['values'][1]
                except IndexError:
                    self.name = ''
                except ValueError:
                    self.name = ''
            elif field['id'] == 284:
                try:
                    self.number_order = field['value']
                except KeyError:
                    self.number_order = ''
            elif field['id'] == 285:
                try:
                    self.dt = field['value']
                except KeyError:
                    self.dt = ''
            elif field['id'] == 286:
                try:
                    self.tm = field['value']
                except KeyError:
                    self.tm = ''
            elif field['id'] == 280:
                try:
                    value = field['value']
                    self.type_order = value['choice_names'][0]
                except IndexError:
                    self.type_order = ''
                except KeyError:
                    self.type_order = ''
            elif field['id'] == 13:
                try:
                    value = field['value']['fields']
                except KeyError:
                    value = []
                for fld_value in value:
                    if fld_value['id'] == 142:
                        try:
                            self.grade = fld_value['value']
                        except KeyError:
                            self.grade = 0
                    elif fld_value['id'] == 143:
                        try:
                            self.comment = fld_value['value']
                        except KeyError:
                            self.comment = ''
                    elif fld_value['id'] == 144:
                        try:
                            checked = fld_value['value']['fields']
                        except KeyError:
                            checked = []
                        for check in checked:
                            if check['value'] == 'checked':
                                self.checker = check['name']
                            else:
                                self.checker = ''
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
                                if name_prob in self.problem:
                                    pass
                                else:
                                    self.problem.append(name_prob)
                            except KeyError:
                                pass
                            except IndexError:
                                pass

async def work_tickets(order, token, form, catalogs, dt_start, dt_end):
    data_catalog = []
    for uuid in order['uuid']:
        data_catalog.append(str(catalogs[uuid.upper()]))
    item_id = ','.join(data_catalog)
    code = order['country']
    if code == 'ru' or code == 'kz':
        data = {
            "field_ids": [1, 60, 57, 198, 13, 222, 37, 202, 196, 204, 203, 2, 261, 262, 134],
            "include_archived": "y",
            "created_after": dt_start + 'Z',
            "created_before": dt_end + 'Z',
            "fld198": item_id
        }
    else:
        data = {
            "field_ids": [53, 59, 60, 61, 55, 11, 63, 44, 48, 49, 50],
            "include_archived": "y",
            "created_after": dt_start + 'Z',
            "created_before": dt_end + 'Z',
            "fld53": item_id
        }
    try:
        pyrus = await pyrus_api(f'https://api.pyrus.com/v4/forms/{form["FormId"]}/register',
                                token['access_token'], data)
    except KeyError:
        pyrus = {}
    try:
        tasks = pyrus['tasks']
    except KeyError:
        tasks = []
    for task in tasks:
        id_task = task['id']
        tickets = await pyrus_api(f'https://api.pyrus.com/v4/tasks/{id_task}', token['access_token'])
        try:
            ticket = tickets['task']
            fields = ticket['fields']
        except KeyError:
            fields = []
        tick = Ticket()
        if order['country'] == 'ru' or order['country'] == 'kz':
            await tick.get_ticket_ru_kz(fields)
        else:
            await tick.get_ticket_all(fields)
        if tick.checker or tick.comment or tick.problem:
            try:
                time_tz = (datetime.strptime(f'{tick.dt} {tick.tm}', '%Y-%m-%d %H:%M') +
                           timedelta(hours=order['timezone']))
                dt_tz = datetime.strftime(time_tz, '%H:%M %d.%m.%Y')
            except ValueError:
                dt_tz = ''
            prb = ', '.join(tick.problem)
            message = f'\U0001F4AC Тикет от клиента\n\n' \
                      f'<b>Оценка: {tick.grade}</b>\n' \
                      f'Заведение: {tick.name}\n' \
                      f'Номер заказа: {tick.number_order}\n' \
                      f'Тип заказа: {tick.type_order}\n' \
                      f'Проблемы: {prb}\n' \
                      f'Комментарии: {tick.comment}\n' \
                      f'Дата и время заказа: {dt_tz}\n'
            if prb == '':
                message = message.replace('Проблемы: \n', '')
            if tick.comment == '':
                message = message.replace('Комментарии: \n', '')
            if dt_tz == '':
                message = message.replace('Дата и время заказа: \n', '')
            return message


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
    dt_start = datetime.strftime(dt - timedelta(minutes=5), '%Y-%m-%dT%H:%M:%S')
    dt_end = datetime.strftime(dt, '%Y-%m-%dT%H:%M:%S')
    for country in cfg.catalogs_ru:
        value = cfg.catalogs_ru[country]
        try:
            catalogs = await pyrus_api(f'https://api.pyrus.com/v4/catalogs/{value["CatalogId"]}',
                                       token['access_token'])
        except KeyError:
            catalogs = {}
            logger.error(f'ERROR for token in - {country}')
        try:
            for catalog in catalogs['items']:
                dict_catalog[catalog['values'][0]] = catalog['item_id']
        except KeyError:
            logger.error(f'ERROR for catalog in - {country}')
    for order in orders:
        form_id = cfg.catalogs_ru[order['country']]
        message = await work_tickets(order, token, form_id, dict_catalog, dt_start, dt_end)
        await send.sending(order['chat_id'], message, logger, order['id'])
    await pool.close()
