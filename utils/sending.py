from configuration.conf import Config
from aiogram.utils.exceptions import BotBlocked, MigrateToChat, BotKicked, \
    CantParseEntities, ChatNotFound, CantInitiateConversation, Unauthorized
from bot.keyboard import KeyStats


async def sending_couriers(chat, message, order, uuid, tz, logger):
    cfg = Config()
    try:
        if order != '':
            key = KeyStats(order, uuid, tz)
            await cfg.bot.send_message(chat, message, reply_markup=key.stats)
        else:
            await cfg.bot.send_message(chat, message)
    except CantParseEntities as e:
        logger.error(f'ERROR - {e} - {chat}')
    except BotBlocked as e:
        logger.error(f'ERROR - {e} - {chat}')
    except MigrateToChat as e:
        logger.error(f'ERROR - {e} - {chat}')
    except BotKicked as e:
        logger.error(f'ERROR - {e} - {chat}')
    except ChatNotFound as e:
        logger.error(f'ERROR - {e} - {chat}')
    except CantInitiateConversation as e:
        logger.error(f'ERROR - {e} - {chat}')
    except Unauthorized as e:
        logger.error(f'ERROR - {e} - {chat}')


async def sending(chat, message, logger):
    cfg = Config()
    try:
        await cfg.bot.send_message(chat, message)
    except CantParseEntities as e:
        logger.error(f'ERROR - {e} - {chat}')
    except BotBlocked as e:
        logger.error(f'ERROR - {e} - {chat}')
    except MigrateToChat as e:
        logger.error(f'ERROR - {e} - {chat}')
    except BotKicked as e:
        logger.error(f'ERROR - {e} - {chat}')
    except ChatNotFound as e:
        logger.error(f'ERROR - {e} - {chat}')
    except CantInitiateConversation as e:
        logger.error(f'ERROR - {e} - {chat}')
    except Unauthorized as e:
        logger.error(f'ERROR - {e} - {chat}')
