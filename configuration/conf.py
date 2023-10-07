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
    scope = 'staffmembers:read email employee phone profile ext_profile openid stopsales deliverystatistics staffshifts:read productionefficiency ' \
            'accounting user.role:read shared marketplacesubscription:read offline_access'
    redirect = os.getenv('REDIRECT')
    verifier = os.getenv('VERIFIER')
    client = os.getenv('CLIENT')
    secret = os.getenv('SECRET')
    dp = Dispatcher(bot, storage=MemoryStorage())
    scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Europe/Moscow', 'apscheduler.job_defaults.max_instances': 4})
    catalogs = {
        "ru": {
            "FormId": 522023,
            "CatalogId": 56873,
        },
        "kz": {
            "FormId": 522023,
            "CatalogId": 56873,
        },
        "by": {     # Нет доступа к проекту 824654.
            "FormId": 824654,
            "CatalogId": 30499,
        },
        "ro": {     # На форме с id 831570 и названием CustomerSupport [RO] не существует поля с id 198.
            "FormId": 831570,
            "CatalogId": 90866
        },
        "gb": {     # На форме с id 682797 и названием CustomerSupport [UK] не существует поля с id 198.
            "FormId": 682797,
            "CatalogId": 60149
        },
        "lt": {     # На форме с id 838124 и названием CustomerSupport [LT] не существует поля с id 198.
            "FormId": 838124,
            "CatalogId": 70148
        },
        "ee": {     # На форме с id 838123 и названием CustomerSupport [EE] не существует поля с id 198.
            "FormId": 838123,
            "CatalogId": 70149
        },
        "ng": {     # На форме с id 838126 и названием CustomerSupport [NG] не существует поля с id 198.
            "FormId": 838126,
            "CatalogId": 77510
        },
        "de": {     # На форме с id 829106 и названием CustomerSupport [DE] не существует поля с id 198.
            "FormId": 829106,   # Поле Contact Type (id 60) на форме с id 829106 и названием CustomerSupport [DE] удалено.
            "CatalogId": 91121
        },
        "si": {     # На форме с id 838125 и названием CustomerSupport [SL] не существует поля с id 198.
            "FormId": 838125,
            "CatalogId": 92088
        },
        "kg": {     # На форме с id 904908 и названием CustomerSupport [KG] - PROD не существует поля с id 198.
            "FormId": 904908,
            "CatalogId": 109717
        },
        "uz": {     # На форме с id 904910 и названием CustomerSupport [UZ] - PROD не существует поля с id 198.
            "FormId": 904910,
            "CatalogId": 109716
        },
        "pl": {     # На форме с id 931511 и названием CustomerSupport [PL] - PROD не существует поля с id 198.
            "FormId": 931511,
            "CatalogId": 115504
        },
        "vn": {     # На форме с id 934385 и названием CustomerSupport [VN] - PROD не существует поля с id 198.
            "FormId": 934385,
            "CatalogId": 116231
        },
        "tj": {     # На форме с id 982830 и названием CustomerSupport [TJ] не существует поля с id 198.
            "FormId": 982830,
            "CatalogId": 127311
        },
        "cz": {     # На форме с id 1028021 и названием CustomerSupport [CZ] - PROD не существует поля с id 198.
            "FormId": 1028021,
            "CatalogId": 134140
        },
        "sk": {     # На форме с id 1028027 и названием CustomerSupport [SK] - PROD не существует поля с id 198.
            "FormId": 1028027,
            "CatalogId": 134145
        },
        "ae": {     # На форме с id 1163909 и названием CustomerSupport [UAE] не существует поля с id 198.
            "FormId": 1163909,
            "CatalogId": 164873
        },
        "am": {     # Поле С каким продуктом это связано? (id 60) на форме с id 1277662 и названием CustomerSupport [AM] удалено.
            "FormId": 1277662,  # На форме с id 1277662 и названием CustomerSupport [AM] не существует поля с id 198.
            "CatalogId": 187001
        },
        "tr": {     # Поле Промокод (id 60) на форме с id 1296836 и названием CustomerSupport [TR] удалено.
            "FormId": 1296836, # На форме с id 1296836 и названием CustomerSupport [TR] не существует поля с id 198.
            "CatalogId": 191688
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
