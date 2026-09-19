"""Shared booths test fixtures."""

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User


@pytest.fixture
def me(db):
    return User.objects.create(kakao_id=990001, nickname="테스트유저")


@pytest.fixture
def auth_client(me):
    client = APIClient()
    client.force_authenticate(user=me)
    return client
