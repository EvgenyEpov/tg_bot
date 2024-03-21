from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]


@dataclass
class Config_tg:
    tg_bot: TgBot


def load_tg_config(path: str | None = None):
    env = Env()
    env.read_env(path)
    return Config_tg(tg_bot=TgBot(
        token=env('BOT_TG_TOKEN'),
        admin_ids=list(map(int, env.list('ADMIN_IDS')))))
