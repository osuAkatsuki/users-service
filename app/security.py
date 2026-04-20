import hashlib
import re
import secrets

import bcrypt
import email_validator

VALID_USERNAME_REGEX = re.compile(r"^[A-Za-z0-9 _\[\]-]{2,15}$")

FORBIDDEN_NORMALIZED_USERNAMES = frozenset(
    {
        # fmt: off
        "nathan_on_osu", "wiltchq", "mathyu", "astar", "the_poon", "mbmasher", "tasuke912", "gosy777",
        "curry3521", "ttobas", "vaxei", "andrea", "cyclone", "child", "c_o_i_n", "obtio", "hvick225",
        "fly_a_kite", "musty", "thepoon", "rbrat3", "rustbell", "goldenwolf", "whitecat", "ozzyozrock",
        "yuko-", "spectator", "vettel", "paparkes", "a_blue", "haruki", "cherry_blossom", "echo",
        "vinno", "akali", "nathan", "ameo", "lifeline", "willcookie", "sharingan33", "arcin", "ktgster",
        "entozer", "zoom", "maxim_bogdan", "[toy]", "seouless", "karthy", "asphyxia", "ztrot", "ppy",
        "bartek22830", "flyte", "ner0", "ely", "unspoken_mattay", "parkes", "fieryrage", "totoki",
        "millhioref", "kaguya", "chal", "s1ck", "captin1", "cryo[iceeicee]", "trafis", "zerrah",
        "bikko", "varvalian", "axarious", "wubwoofwolf", "vamhi", "doomsday", "hdhr", "mismagius",
        "nara", "val0108", "rafis", "digidrake", "chocomint", "doorfin", "thevileone", "xilver",
        "cptnxn", "handsome", "badeu", "sayonara-bye", "crystal", "a12456", "relaxingtuna", "flyingtuna",
        "09kami", "spare", "cmyui", "solis", "coletaku", "zeluar", "nejzha", "_ryuk", "parky",
        "loli_silica", "guy", "barkingmaddog", "thelewa", "nekodex", "paraqeet", "dustice", "justice",
        "cpugeek", "azer", "reimu-desu", "o9kami", "koreapenguin", "cookiezi", "mrekk", "vert", "xeltol",
        "ekoro", "sharpil", "frostidrinks", "firedigger", "ebenezer", "eb", "smoothieworld", "-gn",
        "rbrat3", "happystick", "woey", "clsw", "klug", "firebat92", "blaizer", "fantazy", "elysion",
        "alumentorz", "arfung", "micca", "shayell", "cxu", "itswinter", "ephemeral", "kochiya",
        "cinia_pacifica", "parkourwizard", "cursordance", "hollow_wings", "andros", "sakura", "velperk",
        "loctav", "gasha", "recia", "kroytz", "halfslashed", "skyapple", "okinamo", "murmurtwins",
        "knalli", "kloyd", "yaong", "roma4ka", "damnae", "miniature_lamp", "daniel", "raikozen",
        "torahiko", "fartownik", "tatsumaki", "niko", "mm201", "osuplayer111", "mikuia", "karen",
        "ggm9", "azerite", "dereban", "rohulk", "11t", "nameless_player", "mathi", "professionalbox",
        "fgsky", "sing", "dsan", "ritzeh", "ruri", "ascendence", "kynan", "remillia", "solomon",
        "la_valse", "fenrir", "beasttrollmc", "-ristuki", "deadbeat", "boggles", "idke", "emilia",
        "my_aim_sucks", "sharpli", "snowwhite", "skystar", "daru", "shiiiiiii", "hotzi6",
        "joueur_de_visee", "yelle", "qsc20010", "adamqs", "rrtyui", "jakads", "hentai", "alumetri",
        "morgn", "nero", "idealism", "rucker", "aika", "dunois", "pishifat", "ted", "tom94",
        "mysliderbreak", "azr8", "monstrata", "emperorpenguin83", "dusk", "rumoi", "tillerino",
        "bad_girl", "sharpii", "-hibiki-", "smoogipoooo", "firstus", "peppy", "danyl", "bahamete",
        "kalzo", "nanaya", "angelsim", "banchobot", "marcin", "toybot", "phabled", "abcdullah", "mattay",
        "srchispa", "konnan", "_index", "shigetora", "gayzmcgee", "_yu68", "djpop", "eriksu", "kablaze",
        "sharpll", "kaoru", "asecretbox", "tiger_claw", "toy", "windshear", "avenging_goose",
        "spajder", "exgon", "jhlee0133", "merami", "ralidea", "filsdelama", "zyph", "yuudachi",
        "blue_dragon", "fort", "notititititi", "mcy4", "zallius", "walkingtuna", "kuu01",
        # fmt: on
    },
)


def hash_osu_password(password: str) -> str:
    return bcrypt.hashpw(
        password=hashlib.md5(
            password.encode(),
            usedforsecurity=False,
        )
        .hexdigest()
        .encode(),
        salt=bcrypt.gensalt(),
    ).decode()


def check_osu_password(
    *,
    untrusted_password: str,
    hashed_password: str,
) -> bool:
    return bcrypt.checkpw(
        password=hashlib.md5(
            untrusted_password.encode(),
            usedforsecurity=False,
        )
        .hexdigest()
        .encode(),
        hashed_password=hashed_password.encode(),
    )


def generate_unhashed_secure_token() -> str:
    return secrets.token_urlsafe(nbytes=32)


def hash_secure_token(unhashed_secure_token: str) -> str:
    return hashlib.md5(
        unhashed_secure_token.encode(),
        usedforsecurity=False,
    ).hexdigest()


def validate_username(username: str, /) -> bool:
    """
    Validates that the username meets the security requirements.
    - Must be between 2 and 15 characters long
    - Must contain only alphanumeric characters, spaces, underscores, brackets, and hyphens
    - Must not contain both spaces and underscores
    - Must not be in the list of forbidden usernames
    """
    if not VALID_USERNAME_REGEX.match(username):
        return False
    if " " in username and "_" in username:
        return False
    if username.lower().replace(" ", "_") in FORBIDDEN_NORMALIZED_USERNAMES:
        return False
    return True


def validate_password(password: str, /) -> bool:
    """
    Validates that the password meets the security requirements.
    - Must be at least 8 characters long
    - Must contain at least one digit
    - Must contain at least one uppercase letter
    - Must contain at least one lowercase letter
    """
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.islower() for char in password):
        return False
    return True


def validate_email_address(email_address: str, /) -> bool:
    """
    Validates that the email address meets the security requirements.
    - Must be a valid email format
    """
    try:
        email_validator.validate_email(email_address)
    except email_validator.EmailNotValidError:
        return False
    else:
        return True
