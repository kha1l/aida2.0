from configuration.conf import Config
from aiogram.utils.exceptions import BotBlocked, MigrateToChat, BotKicked, \
    CantParseEntities, ChatNotFound, CantInitiateConversation, Unauthorized, MessageIsTooLong
from bot.keyboard import KeyStats, KeyHide


async def sending_stationary(chat, message, order, uuid, tz, logger):
    cfg = Config()
    try:
        if order != '':
            key = KeyStats(order, uuid, tz)
            await cfg.bot.send_message(chat, message, reply_markup=key.stationary)
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


async def sending_function(message, chat, logger):
    cfg = Config()
    try:
        await cfg.bot.send_message(chat, message, reply_markup=KeyHide.hide)
    except MessageIsTooLong:
        for x in range(0, len(message), 4096):
            try:
                await cfg.bot.send_message(chat, message[x:x + 4096], reply_markup=KeyHide.hide)
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
