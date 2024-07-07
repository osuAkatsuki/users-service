from enum import IntFlag
from enum import IntEnum

class UserPrivileges(IntFlag):
    USER_PUBLIC = 1 << 0
    USER_NORMAL = 1 << 1
    USER_DONOR = 1 << 2
    ADMIN_ACCESS_RAP = 1 << 3
    ADMIN_MANAGE_USERS = 1 << 4
    ADMIN_BAN_USERS = 1 << 5
    ADMIN_SILENCE_USERS = 1 << 6
    ADMIN_WIPE_USERS = 1 << 7
    ADMIN_MANAGE_BEATMAPS = 1 << 8
    ADMIN_MANAGE_SERVER = 1 << 9
    ADMIN_MANAGE_SETTINGS = 1 << 10
    ADMIN_MANAGE_BETA_KEYS = 1 << 11
    ADMIN_MANAGE_REPORTS = 1 << 12
    ADMIN_MANAGE_DOCS = 1 << 13
    ADMIN_MANAGE_BADGES = 1 << 14
    ADMIN_VIEW_RAP_LOGS = 1 << 15
    ADMIN_MANAGE_PRIVILEGES = 1 << 16
    ADMIN_SEND_ALERTS = 1 << 17
    ADMIN_CHAT_MOD = 1 << 18
    ADMIN_KICK_USERS = 1 << 19
    USER_PENDING_VERIFICATION = 1 << 20
    USER_TOURNAMENT_STAFF = 1 << 21
    ADMIN_CAKER = 1 << 22
    USER_PREMIUM = 1 << 23


class UserPlayStyle(IntFlag):
    MOUSE = 1 << 0
    TABLET = 1 << 1
    KEYBOARD = 1 << 2
    TOUCHSCREEN = 1 << 3
    SPOON = 1 << 4
    LEAP_MOTION = 1 << 5
    OCULUS_RIFT = 1 << 6
    DICK = 1 << 7
    EGGPLANT = 1 << 8


class GameMode(IntEnum):
    OSU = 0
    TAIKO = 1
    CATCH = 2
    MANIA = 3


class RelaxMode(IntEnum):
    VANILLA = 0
    RELAX = 1
    AUTOPILOT = 2


class Mode(IntEnum):
    OSU = 0
    TAIKO = 1
    CATCH = 2
    MANIA = 3

    RELAX_OSU = 4
    RELAX_TAIKO = 5
    RELAX_CATCH = 6

    AUTOPILOT_OSU = 8

    @staticmethod
    def from_game_mode_and_relax_mode(
        game_mode: GameMode,
        relax_mode: RelaxMode,
    ) -> "Mode":
        if relax_mode is RelaxMode.VANILLA:
            return Mode(game_mode.value)
        elif relax_mode is RelaxMode.RELAX and game_mode is not GameMode.MANIA:
            return Mode(game_mode.value + 4)
        elif relax_mode is RelaxMode.AUTOPILOT and game_mode is GameMode.OSU:
            return Mode.AUTOPILOT_OSU
        else:
            raise ValueError("Unknown game_mode and relax_mode combo")
