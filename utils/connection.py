from aiohttp.client_exceptions import ContentTypeError
import aiohttp
from configuration.conf import Settings, Config
from loggs.logger import Log
import asyncio


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


async def post_api(url, access, **kwargs) -> dict:
    data = {}
    logger = Log('API')
    retry_limit = 5
    retry_delay = 30
    for key, value in kwargs.items():
        if key == '_from':
            data['from'] = value
        else:
            data[key] = value
    headers = {
        "user-agent": 'DodoVkus',
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Bearer {access}"
    }
    async with aiohttp.ClientSession() as session:
        for i in range(retry_limit):
            async with session.get(url, headers=headers, params=data) as response:
                try:
                    if response.status == 200:
                        response = await response.json()
                        return response
                    elif response.status == 429:
                        logger.info(f'RETRY post_api - {response}')
                        await asyncio.sleep(retry_delay)
                    else:
                        logger.error(f'ERROR post_api - {response}')
                        break
                except ContentTypeError:
                    logger.error(f'ERROR post_api - {response}')
                    return {}
        return {}


async def public_api(url) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            try:
                response = await response.json()
                return response
            except ContentTypeError:
                return {}


async def pyrus_auth():
    cfg = Config()
    url = 'https://api.pyrus.com/v4/auth'
    headers = {
        'Content-Type': 'application/json',
        'user-agent': 'DodoVkus'
    }
    data = {
        "login": cfg.pyrus,
        "security_key": cfg.key
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            try:
                response = await response.json()
                return response
            except ContentTypeError:
                return {}

async def pyrus_api(url, access, *args):
    headers = {
        "Authorization": f'Bearer {access}',
        "Content-Type": "application/json",
        "user-agent": 'DodoVkus'
    }
    async with aiohttp.ClientSession() as session:
        if args:
            async with session.post(url, json=args[0], headers=headers) as response:
                try:
                    response = await response.json()
                    return response
                except ContentTypeError:
                    return {}
        else:
            async with session.get(url, headers=headers) as response:
                try:
                    response = await response.json()
                    return response
                except ContentTypeError:
                    return {}
