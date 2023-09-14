from configuration.conf import Settings
import aiohttp
from aiohttp.client_exceptions import ContentTypeError
from loggs.logger import Log
import jwt


class DataUser:
    name = None
    email = None
    phone = None
    given_name = None
    middle_name = None
    family_name = None
    concept = None
    country = None
    subs = {}

    def __init__(self, access: str):
        self.access = access
        self.logger = Log('GET DATAUSER')
        self.headers = Settings().headers

    async def get_person(self):
        headers = self.headers
        headers["Authorization"] = f"Bearer {self.access}"
        async with aiohttp.ClientSession() as session:
            async with session.post('https://auth.dodois.io/connect/userinfo',
                                    headers=headers) as response:
                try:
                    resp = await response.json()
                    self.name = resp['name']
                    try:
                        self.email = resp['email']
                    except KeyError:
                        pass
                    try:
                        self.phone = resp['phone_number']
                    except KeyError:
                        pass
                    try:
                        self.given_name = resp['given_name']
                    except KeyError:
                        pass
                    try:
                        self.family_name = resp['family_name']
                    except KeyError:
                        pass
                    try:
                        self.middle_name = resp['middle_name']
                    except KeyError:
                        pass
                    try:
                        self.concept = resp['d:tntnm']
                    except KeyError:
                        pass
                    try:
                        self.country = resp['d:cid']
                    except KeyError:
                        pass
                except ContentTypeError:
                    self.logger.error(f'get_datauser - {response} - {self.access}')
                    pass

    async def get_subs(self):
        headers = self.headers
        headers["Authorization"] = f"Bearer {self.access}"
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.dodois.io/marketplace/subscriptions',
                                   headers=headers) as response:
                try:
                    resp = await response.json()
                    for sub in resp['activeUserSubscriptions']:
                        for unit in sub['units']:
                            self.subs[unit] = (sub['tariffAlias'], sub['expiresAt'])
                    return self.subs
                except ContentTypeError:
                    self.logger.error(f'get_datauser - {response} - {self.access}')
                    return self.subs
                except KeyError:
                    self.logger.error(f'get_datauser - {response} - {self.access}')
                    return self.subs


class Users:
    access = None
    refresh = None
    sub = None

    def __init__(self, code: str):
        self.code = code

    async def get_tokens(self):
        logger = Log('GET TOKEN')
        settings = Settings()
        settings.data['code'] = self.code
        async with aiohttp.ClientSession() as session:
            async with session.post('https://auth.dodois.io/connect/token', data=settings.data,
                                    headers=settings.headers) as response:
                try:
                    resp = await response.json()
                    self.access = resp['access_token']
                    self.refresh = resp['refresh_token']
                    jw = jwt.decode(resp['id_token'], options={'verify_signature': False})
                    self.sub = jw['sub']
                except ContentTypeError:
                    logger.error(f'get_tokens - {response} - {self.code}')
                    pass
                except KeyError:
                    logger.error(f'get_tokens_KEY_ERROR - {response} - {self.code}')
                    pass
