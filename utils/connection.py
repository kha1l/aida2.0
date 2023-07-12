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

    async def get_subscriptions(self, **kwargs):
        logger = Log('CONNECT')
        settings = Settings()
        settings.headers['Authorization'] = f"Bearer {kwargs['access']}"
        try:
            self.response = {
                'activeUserSubscriptions': [
                    {
                        "units": [
                            "000d3a240c719a8711e68aba13f81faa",
                            "000d3a240c719a8711e68aba13f8fdb7",
                            "000d3a240c719a8711e68aba13f8ffd4"
                        ],
                        "expiresAt": "2026-09-02T18:40:21",
                        "tariffAlias": "free"
                    },
                    {
                        "units": [
                            "000d3a240c719a8711e68aba13f9fdb2",
                            "000d3a23b0dc80dc11e750dd6e1e61e0",
                            "000d3a2155a180e411e79c94155e4fa5",
                        ],
                        "expiresAt": "2023-07-12T19:40:21",
                        "tariffAlias": "standard"
                    },
                    {
                        "units": [
                            "000d3a26b5b080f311e7cdbfab091e32",
                            "000d3a258645a95411e82cde7632a0cf",
                            "000d3a29ff6ba94411e8a9d1e5f6ea20"
                        ],
                        "expiresAt": "2023-07-12T18:40:21",
                        "tariffAlias": "premium"
                    },
                    {
                        "units": [
                            "000d3a24d2b7a94311e8bd9d5101a4b5",
                            "000d3a22fa54a81511ea943d4bba8970",
                            "000d3aac9dcabb2e11ebefc4a7c197b4",
                            "000d3abf84c3bb3011ecba49c5526cbd"
                        ],
                        "expiresAt": "2023-07-12T17:58:21",
                        "tariffAlias": "luxury"
                    }
                ]
            }
            return self.response
        except ContentTypeError:
            logger.error(f"ERROR subscriptions - {self.response} - {kwargs['access']}")
            return {}
