class BotHolder:
    _bot_instance = None

    @classmethod
    def set_bot(cls, bot):
        cls._bot_instance = bot

    @classmethod
    def get_bot(cls):
        return cls._bot_instance
