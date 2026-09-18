import pytest

from apps.admins.models import Admin
from apps.notices.models import Notice


@pytest.mark.django_db
class TestNoticeModel:
    def test_create_notice_with_defaults(self):
        notice = Notice.objects.create(
            title="축제 안내 공지",
            content="축제가 곧 시작됩니다.",
        )
        assert notice.id is not None
        assert notice.type == Notice.Type.NORMAL
        assert notice.title == "축제 안내 공지"
        assert notice.content == "축제가 곧 시작됩니다."
        assert notice.image_url is None
        assert notice.admin is None
        assert notice.deleted_at is None
        assert str(notice) == "[일반] 축제 안내 공지"

    def test_create_urgent_notice_with_admin_and_image(self):
        admin = Admin.objects.create(admin_key="secret-key-123", name="총괄관리자")
        notice = Notice.objects.create(
            admin=admin,
            type=Notice.Type.URGENT,
            title="우천으로 인한 일정 변경",
            content="공연 시간이 1시간 지연됩니다.",
            image_url="https://example.com/notice.jpg",
        )
        assert notice.type == Notice.Type.URGENT
        assert notice.admin == admin
        assert notice.image_url == "https://example.com/notice.jpg"
        assert str(notice) == "[긴급] 우천으로 인한 일정 변경"

    def test_soft_delete_and_querysets(self):
        notice = Notice.objects.create(
            title="삭제 테스트 공지",
            content="삭제될 예정입니다.",
        )
        assert Notice.objects.alive().count() == 1

        # Soft delete via queryset
        Notice.objects.filter(id=notice.id).soft_delete()
        notice.refresh_from_db()

        assert notice.deleted_at is not None
        assert Notice.objects.alive().count() == 0
        assert Notice.objects.filter(id=notice.id).exists()
