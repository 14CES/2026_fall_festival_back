import pytest

from apps.notices.models import Notice

NOTICES_URL = "/api/notices/"


@pytest.mark.django_db
class TestAdminNoticeUpdateAPI:
    def test_unauthorized_access_denied(self, client):
        notice = Notice.objects.create(title="공지", content="본문")
        response = client.put(
            f"{NOTICES_URL}{notice.id}/",
            data={"title": "수정", "content": "수정", "type": "NORMAL"},
            content_type="application/json",
        )
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "UNAUTHORIZED"

    def test_update_notice_success(self, client, auth_headers):
        notice = Notice.objects.create(
            title="기존 공지 제목",
            content="기존 공지 본문",
            type=Notice.Type.NORMAL,
        )
        assert notice.updated_at is None

        payload = {
            "title": "[수정] 긴급 공지사항",
            "content": "수정된 공지 내용입니다.",
            "type": "URGENT",
            "image_url": "https://example.com/updated.jpg",
        }

        response = client.put(
            f"{NOTICES_URL}{notice.id}/",
            data=payload,
            content_type="application/json",
            **auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["code"] == "ADMIN_NOTICE_UPDATE_SUCCESS"
        assert data["data"]["title"] == "[수정] 긴급 공지사항"
        assert data["data"]["content"] == "수정된 공지 내용입니다."
        assert data["data"]["type"] == "URGENT"
        assert data["data"]["image_url"] == "https://example.com/updated.jpg"
        assert data["data"]["updated_at"] is not None

        # Verify in DB
        notice.refresh_from_db()
        assert notice.title == "[수정] 긴급 공지사항"
        assert notice.type == Notice.Type.URGENT
        assert notice.updated_at is not None

    def test_update_notice_not_found(self, client, auth_headers):
        payload = {
            "title": "수정 제목",
            "content": "수정 내용",
            "type": "NORMAL",
        }
        response = client.put(
            f"{NOTICES_URL}99999/",
            data=payload,
            content_type="application/json",
            **auth_headers,
        )
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "NOT_FOUND"

    def test_update_soft_deleted_notice_fails(self, client, auth_headers):
        notice = Notice.objects.create(title="삭제된 공지", content="본문")
        Notice.objects.filter(id=notice.id).soft_delete()

        payload = {
            "title": "수정 시도",
            "content": "수정 시도",
            "type": "NORMAL",
        }
        response = client.put(
            f"{NOTICES_URL}{notice.id}/",
            data=payload,
            content_type="application/json",
            **auth_headers,
        )
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "NOT_FOUND"

    def test_update_notice_empty_title_fails(self, client, auth_headers):
        notice = Notice.objects.create(title="공지", content="본문")
        payload = {
            "title": "   ",
            "content": "수정 내용",
            "type": "NORMAL",
        }
        response = client.put(
            f"{NOTICES_URL}{notice.id}/",
            data=payload,
            content_type="application/json",
            **auth_headers,
        )
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "INVALID_INPUT"
        assert "title" in data["errors"]

    def test_update_notice_invalid_image_url_fails(self, client, auth_headers):
        notice = Notice.objects.create(title="공지", content="본문")
        payload = {
            "title": "수정 제목",
            "content": "수정 내용",
            "type": "NORMAL",
            "image_url": "not-valid-url",
        }
        response = client.put(
            f"{NOTICES_URL}{notice.id}/",
            data=payload,
            content_type="application/json",
            **auth_headers,
        )
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "INVALID_INPUT"
        assert "image_url" in data["errors"]


@pytest.mark.django_db
class TestAdminNoticeDeleteAPI:
    def test_unauthorized_access_denied(self, client):
        notice = Notice.objects.create(title="공지", content="본문")
        response = client.delete(f"{NOTICES_URL}{notice.id}/")
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "UNAUTHORIZED"

    def test_delete_notice_success(self, client, auth_headers):
        notice = Notice.objects.create(title="삭제 대상 공지", content="삭제될 내용")

        response = client.delete(f"{NOTICES_URL}{notice.id}/", **auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["code"] == "ADMIN_NOTICE_DELETE_SUCCESS"

        # Check DB soft delete
        notice.refresh_from_db()
        assert notice.deleted_at is not None
        assert Notice.objects.alive().filter(id=notice.id).exists() is False

    def test_delete_notice_not_found(self, client, auth_headers):
        response = client.delete(f"{NOTICES_URL}99999/", **auth_headers)
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "NOT_FOUND"

    def test_delete_already_deleted_notice_fails(self, client, auth_headers):
        notice = Notice.objects.create(title="이미 삭제된 공지", content="본문")
        Notice.objects.filter(id=notice.id).soft_delete()

        response = client.delete(f"{NOTICES_URL}{notice.id}/", **auth_headers)
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "NOT_FOUND"
