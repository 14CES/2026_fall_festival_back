"""Lost items request and response serializers (read-only, issue #8)."""

from rest_framework import serializers

from common.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

from .selectors import thumbnail_url, top_keywords


class LostItemListQuerySerializer(serializers.Serializer):
    found_date = serializers.DateField(required=False)
    page = serializers.IntegerField(required=False, min_value=0, default=0)
    size = serializers.IntegerField(
        required=False, min_value=1, max_value=MAX_PAGE_SIZE, default=DEFAULT_PAGE_SIZE
    )


def to_list_item(lost_item):
    return {
        "lost_item_id": lost_item.pk,
        "title": lost_item.title,
        "found_date": lost_item.found_date,
        "thumbnail_url": thumbnail_url(lost_item),
        "tags": top_keywords(lost_item),
        "created_at": lost_item.created_at,
    }


def to_detail(lost_item):
    return {
        "lost_item_id": lost_item.pk,
        "title": lost_item.title,
        "found_date": lost_item.found_date,
        "images": [
            {"image_id": image.pk, "image_url": image.image_url, "sort_order": image.sort_order}
            for image in lost_item.alive_images
        ],
        "tags": [
            {"tag_id": tag.pk, "keyword": tag.keyword, "sort_order": tag.sort_order}
            for tag in lost_item.alive_tags
        ],
        "created_at": lost_item.created_at,
        "updated_at": lost_item.updated_at,
    }


# --- 응답 스키마 (Swagger 문서 전용) -------------------------------------------


class LostItemListItemSerializer(serializers.Serializer):
    lost_item_id = serializers.IntegerField()
    title = serializers.CharField()
    found_date = serializers.DateField()
    thumbnail_url = serializers.URLField(allow_null=True)
    tags = serializers.ListField(child=serializers.CharField())
    created_at = serializers.DateTimeField()


class LostItemListDataSerializer(serializers.Serializer):
    total_count = serializers.IntegerField()
    page = serializers.IntegerField()
    size = serializers.IntegerField()
    has_next = serializers.BooleanField()
    items = LostItemListItemSerializer(many=True)


class LostItemListResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    code = serializers.CharField(default="LOST_ITEM_LIST_SUCCESS")
    message = serializers.CharField(default="분실물 목록을 조회했습니다.")
    data = LostItemListDataSerializer()


class LostItemImageSerializer(serializers.Serializer):
    image_id = serializers.IntegerField()
    image_url = serializers.URLField()
    sort_order = serializers.IntegerField()


class LostItemTagSerializer(serializers.Serializer):
    tag_id = serializers.IntegerField()
    keyword = serializers.CharField()
    sort_order = serializers.IntegerField()


class LostItemDetailDataSerializer(serializers.Serializer):
    lost_item_id = serializers.IntegerField()
    title = serializers.CharField()
    found_date = serializers.DateField()
    images = LostItemImageSerializer(many=True)
    tags = LostItemTagSerializer(many=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField(allow_null=True)


class LostItemDetailResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    code = serializers.CharField(default="LOST_ITEM_DETAIL_SUCCESS")
    message = serializers.CharField(default="분실물 정보를 조회했습니다.")
    data = LostItemDetailDataSerializer()