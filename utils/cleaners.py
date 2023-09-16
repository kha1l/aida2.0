from aiogram.utils.exceptions import MessageCantBeDeleted, MessageNotModified, MessageToDeleteNotFound


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

    @staticmethod
    async def delete_markup(call):
        try:
            await call.message.delete_reply_markup()
        except MessageToDeleteNotFound:
            pass

    @staticmethod
    async def edit_markup(call, key):
        try:
            await call.message.edit_reply_markup(reply_markup=key)
        except MessageNotModified:
            pass
