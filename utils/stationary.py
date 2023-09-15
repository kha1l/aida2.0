from utils.connection import Connect
from iso3166 import countries
from loggs.logger import Log
from authorization.users import DataUser


class Units:
    def __init__(self, id):
        self.id = id
        self.units = []

    async def get_units(self, access):
        logger = Log("UNITS")
        conn = Connect()
        try:
            access_units = await conn.get_units(access=access)
            if access_units:
                code = countries.get(access_units[0]['countryCode']).alpha2.lower()
                units_all = await conn.get_public_api(f'https://publicapi.dodois.io/{code}/api/v1/unitinfo/all')
                for units in units_all:
                    for unit in access_units:
                        if unit['id'].upper() == units['UUId'] and units['Type'] == 1 and units['State'] == 1:
                            await self.config_units((unit['name'], units['Id'], unit['id'], code,
                                                     units['TimeZoneShift'], self.id))
                return self.units
        except IndexError:
            logger.error(f"ERROR INDEX - {self.id}")
            return self.units
        except KeyError:
            logger.error(f"ERROR KEY - {self.id}")
            return self.units

    async def config_units(self, data: tuple):
        units = {
            'name': data[0],
            'id': data[1],
            'uuid': data[2],
            'code': data[3],
            'tz': data[4],
            'user_id': data[5]
        }
        self.units.append(units)


async def add_stationary(id, access):
    data = DataUser(access)
    units = Units(id)
    subs = await data.get_subs()
    access_units = await units.get_units(access)
    user_units = []
    for data_units in access_units:
        if data_units['uuid'] in subs:
            data_units['subs'] = subs[data_units['uuid']][0]
            data_units['expires'] = subs[data_units['uuid']][1]
        else:
            data_units['subs'] = 'free'
            data_units['expires'] = 'forever'
        user_units.append(data_units)
    return user_units, subs


class Stationary:

    def __init__(self, input_list):
        self.input_list = input_list

    def process_units(self):
        units = []
        for unit in self.input_list:
            units.append(dict(unit))
        return units
