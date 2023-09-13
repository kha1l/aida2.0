from aiohttp.client_exceptions import ContentTypeError
import aiohttp
from configuration.conf import Settings
from loggs.logger import Log


class Connect:
    def __init__(self):
        self.response = None

    async def get_public_api(self, url) -> dict:
        logger = Log('CONNECT')
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                try:
                    self.response = await resp.json()
                    return self.response
                except ContentTypeError:
                    logger.error(f"ERROR public_api - {self.response}")
                    return {}

    async def get_units(self, **kwargs) -> dict:
        logger = Log('CONNECT')
        settings = Settings()
        settings.headers['Authorization'] = f"Bearer {kwargs['access']}"
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.dodois.io/auth/roles/units',
                                   headers=settings.headers) as resp:
                try:
                    self.response = await resp.json()
                    return self.response
                except ContentTypeError:
                    logger.error(f"ERROR get_units - {self.response} - {kwargs['access']}")
                    return {}
