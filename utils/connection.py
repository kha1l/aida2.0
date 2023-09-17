from aiohttp.client_exceptions import ContentTypeError
import aiohttp
from configuration.conf import Settings, Config
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

    async def update_tokens(self, **kwargs) -> dict:
        logger = Log('UPDATE TOKENS')
        cfg = Config()
        data = {
            'grant_type': 'refresh_token',
            'redirect_uri': cfg.redirect,
            'code_verifier': cfg.verifier,
            'refresh_token': kwargs['refresh']
        }
        headers = {
            "user-agent": 'DodoVkus',
            "Content-Type": "application/x-www-form-urlencoded",
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(kwargs['url'], headers=headers, data=data, allow_redirects=False,
                                    auth=aiohttp.BasicAuth(cfg.client, cfg.secret)) as resp:
                try:
                    self.response = await resp.json()
                    return self.response
                except ContentTypeError:
                    logger.error(f'ERROR update_tokens - {self.response}')
                    return {}
