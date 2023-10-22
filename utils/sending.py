from configuration.conf import Config
from aiogram.utils.exceptions import BotBlocked, MigrateToChat, BotKicked, \
    CantParseEntities, ChatNotFound, CantInitiateConversation, Unauthorized, MessageIsTooLong
from bot.keyboard import KeyStats, KeyHide


class Send:
    def __init__(self, **kwargs):
        self.cfg = Config()
        if kwargs:
            self.db = kwargs['db']
        else:
            self.db = None

    async def sending_statistics(self, chat, message, order, uuid, tz, logger, types, order_id, concept):
        pool = await self.db.create_pool()
        try:
            if order != '':
                key = KeyStats(order, uuid, tz, concept)
                if types == 'rest':
                    keys = key.stationary
                else:
                    keys = key.stats
                await self.cfg.bot.send_message(chat, message, reply_markup=keys)
            else:
                await self.cfg.bot.send_message(chat, message)
        except CantParseEntities as e:
            await self.db.drop_order(pool, order_id)
            logger.error(f'ERROR - {e} - {chat} - {order_id}')
        except BotBlocked as e:
            await self.db.drop_order(pool, order_id)
            logger.error(f'ERROR - {e} - {chat} - {order_id}')
        except MigrateToChat as e:
            await self.db.drop_order(pool, order_id)
            logger.error(f'ERROR - {e} - {chat} - {order_id}')
        except BotKicked as e:
            await self.db.drop_order(pool, order_id)
            logger.error(f'ERROR - {e} - {chat} - {order_id}')
        except ChatNotFound as e:
            await self.db.drop_order(pool, order_id)
            logger.error(f'ERROR - {e} - {chat} - {order_id}')
        except CantInitiateConversation as e:
            await self.db.drop_order(pool, order_id)
            logger.error(f'ERROR - {e} - {chat} - {order_id}')
        except Unauthorized as e:
            await self.db.drop_order(pool, order_id)
            logger.error(f'ERROR - {e} - {chat} - {order_id}')
        await pool.close()

    async def sending_function(self, message, chat, logger):
        try:
            await self.cfg.bot.send_message(chat, message, reply_markup=KeyHide.hide)
        except MessageIsTooLong:
            for x in range(0, len(message), 4096):
                try:
                    await self.cfg.bot.send_message(chat, message[x:x + 4096], reply_markup=KeyHide.hide)
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

    async def sending(self, chat, message, logger, order_id):
        pool = await self.db.create_pool()
        try:
            await self.cfg.bot.send_message(chat, message)
        except CantParseEntities as e:
            await self.db.drop_order(pool, order_id)
            logger.error(f'ERROR - {e} - {chat} - {order_id}')
        except BotBlocked as e:
            await self.db.drop_order(pool, order_id)
            logger.error(f'ERROR - {e} - {chat} - {order_id}')
        except MigrateToChat as e:
            await self.db.drop_order(pool, order_id)
            logger.error(f'ERROR - {e} - {chat} - {order_id}')
        except BotKicked as e:
            await self.db.drop_order(pool, order_id)
            logger.error(f'ERROR - {e} - {chat} - {order_id}')
        except ChatNotFound as e:
            await self.db.drop_order(pool, order_id)
            logger.error(f'ERROR - {e} - {chat} - {order_id}')
        except CantInitiateConversation as e:
            await self.db.drop_order(pool, order_id)
            logger.error(f'ERROR - {e} - {chat} - {order_id}')
        except Unauthorized as e:
            await self.db.drop_order(pool, order_id)
            logger.error(f'ERROR - {e} - {chat} - {order_id}')
        await pool.close()
