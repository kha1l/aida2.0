from aiogram.utils.exceptions import MessageCantBeDeleted, MessageNotModified


class Clean:

    @staticmethod
    async def delete_message(message):
        try:
            await message.delete()
        except MessageCantBeDeleted:
            pass

    @staticmethod
    async def modify_message(message):
        try:
            await message.delete()
        except MessageNotModified:
            pass
