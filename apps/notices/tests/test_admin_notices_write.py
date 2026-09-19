import pytest

from apps.notices.models import Notice

ADMIN_NOTICES_URL = "/api/admin/notices/"


@pytest.mark.django_db
class TestAdminNoticeCreateAPI:
    def test_unauthorized_access_denied(self, client):
        payload = {
            "title": "공지 제목",
            "content": "공지 본문",
        }
        response = client.post(ADMIN_NOTICES_URL, data=payload, content_type="application/json")
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "UNAUTHORIZED"

    def test_create_notice_success_defaults(self, client, auth_headers):
        payload = {
            "title": "축제 시작 안내",
            "content": "축제가 성황리에 시작되었습니다!",
        }
        response = client.post(
            ADMIN_NOTICES_URL,
            data=payload,
            content_type="application/json",
            **auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["code"] == "ADMIN_NOTICE_CREATE_SUCCESS"
        assert data["data"]["title"] == "축제 시작 안내"
        assert data["data"]["content"] == "축제가 성황리에 시작되었습니다!"
        assert data["data"]["type"] == "NORMAL"
        assert data["data"]["image_url"] is None
        assert data["data"]["id"] is not None

        # Verify in DB
        notice = Notice.objects.get(pk=data["data"]["id"])
        assert notice.title == "축제 시작 안내"
        assert notice.type == Notice.Type.NORMAL

    def test_create_urgent_notice_with_image(self, client, auth_headers):
        payload = {
            "title": "[긴급] 일정 변경 안내",
            "content": "비가 와서 실내로 변경됩니다.",
            "type": "URGENT",
            "image_url": "https://example.com/poster.jpg",
        }
        response = client.post(
            ADMIN_NOTICES_URL,
            data=payload,
            content_type="application/json",
            **auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["type"] == "URGENT"
        assert data["data"]["image_url"] == "https://example.com/poster.jpg"

        notice = Notice.objects.get(pk=data["data"]["id"])
        assert notice.type == Notice.Type.URGENT
        assert notice.image_url == "https://example.com/poster.jpg"

    def test_create_notice_missing_title_fails(self, client, auth_headers):
        payload = {
            "content": "제목이 없는 공지",
        }
        response = client.post(
            ADMIN_NOTICES_URL,
            data=payload,
            content_type="application/json",
            **auth_headers,
        )
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "INVALID_INPUT"
        assert "title" in data["errors"]

    def test_create_notice_empty_title_fails(self, client, auth_headers):
        payload = {
            "title": "   ",
            "content": "공백 제목 공지",
        }
        response = client.post(
            ADMIN_NOTICES_URL,
            data=payload,
            content_type="application/json",
            **auth_headers,
        )
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "INVALID_INPUT"
        assert "title" in data["errors"]

    def test_create_notice_missing_content_fails(self, client, auth_headers):
        payload = {
            "title": "본문이 없는 공지",
        }
        response = client.post(
            ADMIN_NOTICES_URL,
            data=payload,
            content_type="application/json",
            **auth_headers,
        )
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "INVALID_INPUT"
        assert "content" in data["errors"]

    def test_create_notice_invalid_type_fails(self, client, auth_headers):
        payload = {
            "title": "유효하지 않은 타입",
            "content": "타입 오류 테스트",
            "type": "INVALID_TYPE",
        }
        response = client.post(
            ADMIN_NOTICES_URL,
            data=payload,
            content_type="application/json",
            **auth_headers,
        )
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "INVALID_INPUT"
        assert "type" in data["errors"]

    def test_create_notice_invalid_image_url_fails(self, client, auth_headers):
        payload = {
            "title": "잘못된 이미지 URL",
            "content": "URL 형식 오류 테스트",
            "image_url": "not-a-valid-url",
        }
        response = client.post(
            ADMIN_NOTICES_URL,
            data=payload,
            content_type="application/json",
            **auth_headers,
        )
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "INVALID_INPUT"
        assert "image_url" in data["errors"]
