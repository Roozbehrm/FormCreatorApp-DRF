from tests.factories import UserFactory


def test_user_factory_creates_active_user(db):
    user = UserFactory()

    assert user.pk is not None
    assert user.email
    assert user.is_active is True
