import pytest

from apps.notices.models import Notice

ADMIN_NOTICES_URL = "/api/notices/"


@pytest.mark.django_db
class TestAdminNoticeListAPI:
    def test_unauthorized_access_denied(self, client):
        response = client.get(ADMIN_NOTICES_URL)
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "UNAUTHORIZED"

    def test_list_notices_urgent_priority_ordering(self, client, auth_headers):
        # Create normal and urgent notices
        normal1 = Notice.objects.create(
            title="일반 공지 1",
            content="내용 1",
            type=Notice.Type.NORMAL,
        )
        urgent1 = Notice.objects.create(
            title="긴급 공지 1",
            content="긴급 내용 1",
            type=Notice.Type.URGENT,
        )
        normal2 = Notice.objects.create(
            title="일반 공지 2",
            content="내용 2",
            type=Notice.Type.NORMAL,
        )

        response = client.get(ADMIN_NOTICES_URL, **auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["code"] == "ADMIN_NOTICE_LIST_SUCCESS"

        items = data["data"]["items"]
        assert len(items) == 3
        # Urgent notice should be at the top
        assert items[0]["id"] == urgent1.id
        assert items[0]["type"] == "URGENT"
        # Normal notices should follow in created_at desc order (normal2 before normal1)
        assert items[1]["id"] == normal2.id
        assert items[2]["id"] == normal1.id

    def test_filter_by_type(self, client, auth_headers):
        Notice.objects.create(title="일반 공지", content="일반", type=Notice.Type.NORMAL)
        Notice.objects.create(title="긴급 공지", content="긴급", type=Notice.Type.URGENT)

        # Filter URGENT
        resp_urgent = client.get(f"{ADMIN_NOTICES_URL}?type=URGENT", **auth_headers)
        assert resp_urgent.status_code == 200
        data_urgent = resp_urgent.json()["data"]
        assert data_urgent["meta"]["total_count"] == 1
        assert data_urgent["items"][0]["type"] == "URGENT"

        # Filter NORMAL
        resp_normal = client.get(f"{ADMIN_NOTICES_URL}?type=NORMAL", **auth_headers)
        assert resp_normal.status_code == 200
        data_normal = resp_normal.json()["data"]
        assert data_normal["meta"]["total_count"] == 1
        assert data_normal["items"][0]["type"] == "NORMAL"

    def test_pagination(self, client, auth_headers):
        for i in range(5):
            Notice.objects.create(
                title=f"공지 {i}",
                content=f"내용 {i}",
                type=Notice.Type.NORMAL,
            )

        response = client.get(f"{ADMIN_NOTICES_URL}?page=0&size=2", **auth_headers)
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data["items"]) == 2
        assert data["meta"]["total_count"] == 5
        assert data["meta"]["page"] == 0
        assert data["meta"]["size"] == 2
        assert data["meta"]["has_next"] is True

    def test_soft_deleted_notices_excluded(self, client, auth_headers):
        active_notice = Notice.objects.create(
            title="활성 공지",
            content="활성 내용",
            type=Notice.Type.NORMAL,
        )
        deleted_notice = Notice.objects.create(
            title="삭제된 공지",
            content="삭제된 내용",
            type=Notice.Type.NORMAL,
        )
        Notice.objects.filter(id=deleted_notice.id).soft_delete()

        response = client.get(ADMIN_NOTICES_URL, **auth_headers)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["meta"]["total_count"] == 1
        assert data["items"][0]["id"] == active_notice.id

    def test_invalid_query_params_returns_400(self, client, auth_headers):
        response = client.get(f"{ADMIN_NOTICES_URL}?type=INVALID_TYPE", **auth_headers)
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "INVALID_INPUT"


@pytest.mark.django_db
class TestAdminNoticeDetailAPI:
    def test_get_notice_detail_success(self, client, auth_headers):
        notice = Notice.objects.create(
            title="상세 조회 테스트",
            content="상세 본문 내용입니다.",
            type=Notice.Type.URGENT,
            image_url="https://example.com/image.jpg",
        )

        response = client.get(f"{ADMIN_NOTICES_URL}{notice.id}/", **auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["code"] == "ADMIN_NOTICE_DETAIL_SUCCESS"
        assert data["data"]["id"] == notice.id
        assert data["data"]["title"] == "상세 조회 테스트"
        assert data["data"]["content"] == "상세 본문 내용입니다."
        assert data["data"]["type"] == "URGENT"
        assert data["data"]["image_url"] == "https://example.com/image.jpg"

    def test_get_notice_detail_not_found(self, client, auth_headers):
        response = client.get(f"{ADMIN_NOTICES_URL}99999/", **auth_headers)
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "NOT_FOUND"

    def test_get_soft_deleted_notice_returns_404(self, client, auth_headers):
        notice = Notice.objects.create(
            title="삭제된 공지",
            content="본문",
            type=Notice.Type.NORMAL,
        )
        Notice.objects.filter(id=notice.id).soft_delete()

        response = client.get(f"{ADMIN_NOTICES_URL}{notice.id}/", **auth_headers)
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "NOT_FOUND"
