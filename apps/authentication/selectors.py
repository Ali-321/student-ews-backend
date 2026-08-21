
from authentication.models import User


def user_get_me_selector(*, user: User) -> User:
    """Selector untuk mengambil instance user yang sedang terautentikasi."""
    return user