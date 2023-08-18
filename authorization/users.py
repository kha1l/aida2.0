from configuration.conf import Settings
import aiohttp
from aiohttp.client_exceptions import ContentTypeError
from loggs.logger import Log
import jwt


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
