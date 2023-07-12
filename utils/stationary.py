from utils.connection import Connect
from iso3166 import countries
from loggs.logger import Log


class Units:
    def __init__(self, user):
        self.user = user
        self.units = []

    async def get_units(self):
        logger = Log("UNITS")
        conn = Connect()
        subs_dict = {}
        try:
            access_units = await conn.get_units(access=self.user[1])
            if access_units:
                code = countries.get(access_units[0]['countryCode']).alpha2.lower()
                subs = await conn.get_subscriptions(access=self.user[1])
                if subs:
                    for sub in subs['activeUserSubscriptions']:
                        for sub_unit in sub['units']:
                            subs_dict[sub_unit] = sub['tariffAlias']
                units_all = await conn.get_public_api(f'https://publicapi.dodois.io/{code}/api/v1/unitinfo/all')
                for units in units_all:
                    for unit in access_units:
                        if unit['id'].upper() == units['UUId'] and units['Type'] == 1 and units['State'] == 1:
                            await self.config_units((unit['name'], units['Id'], unit['id'], code,
                                                     units['TimeZoneShift'], self.user[0], subs_dict[unit['id']]))
                return self.units
        except IndexError:
            logger.error(f"ERROR INDEX - {self.user[0]}")
            return self.units
        except KeyError:
            logger.error(f"ERROR KEY - {self.user[0]}")
            return self.units

    async def config_units(self, data: tuple):
        units = {
            'name': data[0],
            'id': data[1],
            'uuid': data[2],
            'code': data[3],
            'tz': data[4],
            'user_id': data[5],
            'sub': data[6]
        }
        self.units.append(units)
