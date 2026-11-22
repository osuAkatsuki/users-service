import hashlib
import re
import secrets

import bcrypt


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


def validate_password_meets_requirements(password: str, /) -> bool:
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


# Keep reserved names in sync with the legacy website's registration and rename rules.
_RESERVED_USERNAMES = frozenset(
    """
    -gn -hibiki- -ristuki 09kami 11t [toy] _index _ryuk _yu68 a12456 a_blue abcdullah
    adamqs aika akali alumentorz alumetri ameo andrea andros angelsim arcin arfung
    ascendence asecretbox asphyxia astar avenging_goose axarious azer azerite azr8 badeu
    bahamete banchobot barkingmaddog bartek22830 beasttrollmc bikko blaizer blue_dragon
    boggles c_o_i_n captin1 chal cherry_blossom child chocomint cinia_pacifica clsw cmyui
    coletaku cookiezi cptnxn cpugeek cryo[iceeicee] crystal curry3521 cursordance cxu
    cyclone damnae daniel danyl daru deadbeat dereban digidrake djpop doomsday doorfin
    dsan dunois dusk dustice eb ebenezer echo ekoro ely elysion emilia emperorpenguin83
    entozer ephemeral eriksu exgon fantazy fartownik fenrir fgsky fieryrage filsdelama
    firebat92 firedigger firstus fly_a_kite flyingtuna flyte fort frostidrinks gasha
    gayzmcgee ggm9 goldenwolf gosy777 guy halfslashed handsome happystick haruki hdhr
    hentai hollow_wings hotzi6 hvick225 idealism idke itswinter jakads jhlee0133
    joueur_de_visee justice kablaze kaguya kalzo kaoru karen karthy kloyd klug knalli
    kochiya konnan koreapenguin kroytz ktgster kuu01 kynan la_valse lifeline loctav
    loli_silica marcin mathi mathyu mattay maxim_bogdan mbmasher mcy4 merami micca mikuia
    millhioref miniature_lamp mismagius mm201 monstrata morgn mrekk murmurtwins musty
    my_aim_sucks mysliderbreak nameless_player nanaya nara nathan nathan_on_osu nejzha
    nekodex ner0 nero niko notititititi o9kami obtio okinamo osuplayer111 ozzyozrock
    paparkes paraqeet parkes parkourwizard parky peppy phabled pishifat ppy
    professionalbox qsc20010 rafis raikozen ralidea rbrat3 recia reimu-desu relaxingtuna
    remillia ritzeh rohulk roma4ka rrtyui rucker rumoi ruri rustbell s1ck sakura
    sayonara-bye seouless sharingan33 sharpii sharpil sharpli sharpll shayell shigetora
    shiiiiiii sing skyapple skystar smoogipoooo smoothieworld snowwhite solis solomon
    spajder spare spectator srchispa tasuke912 tatsumaki ted the_poon thelewa thepoon
    thevileone tiger_claw tillerino tom94 torahiko totoki toy toybot trafis ttobas
    unspoken_mattay val0108 vamhi varvalian vaxei velperk vert vettel vinno walkingtuna
    whitecat willcookie wiltchq windshear woey wubwoofwolf xeltol xilver yaong yelle
    yuko- yuudachi zallius zeluar zerrah zoom ztrot zyph
    """.split()
)
_USERNAME_PATTERN = re.compile(r"[A-Za-z0-9 _\[\]-]{2,15}")
_EMAIL_PATTERN = re.compile(r'[^\s<>"@]+@[^\s<>"@.]+(?:\.[^\s<>"@.]+)+')


def validate_username(username: str) -> bool:
    return (
        username == username.strip()
        and _USERNAME_PATTERN.fullmatch(username) is not None
        and username.lower().replace(" ", "_") not in _RESERVED_USERNAMES
    )


def validate_email(email: str) -> bool:
    return len(email) <= 254 and _EMAIL_PATTERN.fullmatch(email) is not None
