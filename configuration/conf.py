import os
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher


class Config:
    load_dotenv()
    dbase = os.getenv('DATA_BASE')
    user = os.getenv('USER_NAME')
    password = os.getenv('PASSWORD')
    host = os.getenv('IP')
    token = os.getenv('TOKEN')
    bot = Bot(token, parse_mode='HTML')
    pyrus = os.getenv('PYRUS')
    key = os.getenv('KEY')
    scope = 'staffmembers:read email employee phone profile ext_profile openid stopsales deliverystatistics ' \
            'staffshifts:read productionefficiency accounting user.role:read shared ' \
            'marketplacesubscription:read offline_access'
    redirect = os.getenv('REDIRECT')
    verifier = os.getenv('VERIFIER')
    client = os.getenv('CLIENT')
    secret = os.getenv('SECRET')
    weather_key = os.getenv('API_WEATHER_KEY')
    dp = Dispatcher(bot, storage=MemoryStorage())
    scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Europe/Moscow', 'apscheduler.job_defaults.max_instances': 4})
    catalogs_all = {
        # "by": {
        #     "FormId": 824654,
        #     "CatalogId": 30499,
        # },
        "ro": {
            "FormId": 831570,
            "CatalogId": 90866
        },
        "gb": {
            "FormId": 682797,
            "CatalogId": 60149
        },
        "lt": {
            "FormId": 838124,
            "CatalogId": 70148
        },
        "ee": {
            "FormId": 838123,
            "CatalogId": 70149
        },
        "ng": {
            "FormId": 838126,
            "CatalogId": 77510
        },
        "de": {
            "FormId": 829106,
            "CatalogId": 91121
        },
        "si": {
            "FormId": 838125,
            "CatalogId": 92088
        },
        "kg": {
            "FormId": 904908,
            "CatalogId": 109717
        },
        "uz": {
            "FormId": 904910,
            "CatalogId": 109716
        },
        "pl": {
            "FormId": 931511,
            "CatalogId": 115504
        },
        "vn": {
            "FormId": 934385,
            "CatalogId": 116231
        },
        "tj": {
            "FormId": 982830,
            "CatalogId": 127311
        },
        "cz": {
            "FormId": 1028021,
            "CatalogId": 134140
        },
        "sk": {
            "FormId": 1028027,
            "CatalogId": 134145
        },
        "ae": {
            "FormId": 1163909,
            "CatalogId": 164873
        },
        "am": {
            "FormId": 1277662,
            "CatalogId": 187001
        },
        "tr": {
            "FormId": 1296836,
            "CatalogId": 191688
        }
    }
    catalogs_ru = {
        "ru": {
            "FormId": 522023,
            "CatalogId": 56873,
        },
        "kz": {
            "FormId": 522023,
            "CatalogId": 56873,
        }
    }


class Settings:
    cfg = Config()
    data = {
        'client_id': cfg.client,
        'client_secret': cfg.secret,
        'scope': cfg.scope,
        'grant_type': 'authorization_code',
        'redirect_uri': cfg.redirect,
        'code_verifier': cfg.verifier
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "user-agent": 'DodoVkus',
    }
