
from authentication.models import User
from django.db.models import QuerySet


def user_list_selector(*, role: str = None) -> QuerySet[User]:
    """Selector untuk mengambil daftar user dengan opsi filter role."""
    qs = User.objects.all().order_by("-date_joined")
    if role:
        qs = qs.filter(role=role)
    return qs


def user_get_me_selector(*, user: User) -> User:
    """Selector untuk mengambil instance user yang sedang terautentikasi."""
    return user


