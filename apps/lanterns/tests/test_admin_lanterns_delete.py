import pytest
from django.utils import timezone

from apps.booths.models import Booth
from apps.lanterns.models import Lantern
from apps.lanterns.services import delete_admin_lantern

ADMIN_LANTERNS_URL = "/api/admin/lanterns/"


@pytest.mark.django_db
class TestAdminLanternDeleteAPI:
    def test_unauthorized_access_denied(self, client):
        response = client.delete(f"{ADMIN_LANTERNS_URL}1/")
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "UNAUTHORIZED"

    def test_delete_lantern_success(self, client, auth_headers, test_user, test_booth):
        test_booth.lantern_count = 5
        test_booth.save(update_fields=["lantern_count"])

        lantern = Lantern.objects.create(
            user=test_user,
            booth=test_booth,
            nickname="익명의 코끼리",
            message="삭제될 등불 메시지",
        )

        response = client.delete(f"{ADMIN_LANTERNS_URL}{lantern.id}/", **auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["code"] == "ADMIN_LANTERN_DELETE_SUCCESS"
        assert data["message"] == "등불이 성공적으로 삭제되었습니다."
        assert data["data"] == {}

        # DB 검증
        lantern.refresh_from_db()
        assert lantern.deleted_at is not None
        assert lantern.deleted_by == Lantern.DeletedBy.ADMIN

        test_booth.refresh_from_db()
        assert test_booth.lantern_count == 4

    def test_delete_lantern_count_not_below_zero(self, client, auth_headers, test_user, test_booth):
        test_booth.lantern_count = 0
        test_booth.save(update_fields=["lantern_count"])

        lantern = Lantern.objects.create(
            user=test_user,
            booth=test_booth,
            nickname="익명의 코끼리",
            message="카운트 0 상태 등불",
        )

        response = client.delete(f"{ADMIN_LANTERNS_URL}{lantern.id}/", **auth_headers)
        assert response.status_code == 200

        test_booth.refresh_from_db()
        assert test_booth.lantern_count == 0

    def test_delete_non_existent_lantern_fails(self, client, auth_headers):
        response = client.delete(f"{ADMIN_LANTERNS_URL}999999/", **auth_headers)
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "NOT_FOUND"
        assert "찾을 수 없습니다" in data["message"]

    def test_delete_already_deleted_lantern_fails(
        self, client, auth_headers, test_user, test_booth
    ):
        lantern = Lantern.objects.create(
            user=test_user,
            booth=test_booth,
            nickname="익명의 코끼리",
            message="이미 삭제된 등불",
            deleted_at=timezone.now(),
            deleted_by=Lantern.DeletedBy.USER,
        )

        response = client.delete(f"{ADMIN_LANTERNS_URL}{lantern.id}/", **auth_headers)
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "NOT_FOUND"

    def test_delete_admin_lantern_service_function(self, test_user, test_booth):
        test_booth.lantern_count = 2
        test_booth.save(update_fields=["lantern_count"])

        lantern = Lantern.objects.create(
            user=test_user,
            booth=test_booth,
            nickname="익명의 코끼리",
            message="서비스 함수 직접 테스트",
        )

        delete_admin_lantern(lantern)

        lantern.refresh_from_db()
        assert lantern.deleted_at is not None
        assert lantern.deleted_by == "ADMIN"

        test_booth.refresh_from_db()
        assert test_booth.lantern_count == 1

    def test_delete_admin_lantern_transaction_rollback(self, test_user, test_booth, monkeypatch):
        test_booth.lantern_count = 3
        test_booth.save(update_fields=["lantern_count"])

        lantern = Lantern.objects.create(
            user=test_user,
            booth=test_booth,
            nickname="익명의 코끼리",
            message="트랜잭션 롤백 테스트",
        )

        from apps.lanterns import services

        original_update = Booth.objects.filter

        def mock_filter(*args, **kwargs):
            qs = original_update(*args, **kwargs)

            def mock_update(*u_args, **u_kwargs):
                raise RuntimeError("DB Error during booth update")

            qs.update = mock_update
            return qs

        monkeypatch.setattr(services.Booth.objects, "filter", mock_filter)

        with pytest.raises(RuntimeError, match="DB Error during booth update"):
            services.delete_admin_lantern(lantern)

        # 트랜잭션 롤백으로 인해 lantern 상태가 변경되지 않았는지 검증
        lantern.refresh_from_db()
        assert lantern.deleted_at is None
        assert lantern.deleted_by is None

        test_booth.refresh_from_db()
        assert test_booth.lantern_count == 3
