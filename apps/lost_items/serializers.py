"""분실물 API의 요청/응답 데이터 검증 및 변환.

- 조회(GET) 관련: LostItemListQuerySerializer, to_list_item, to_detail (#8)
- 등록(POST) 관련: LostItemCreateSerializer (#12)
- 나머지는 Swagger 문서에 응답 형태를 보여주기 위한 클래스들
"""

from django.conf import settings
from rest_framework import serializers

from common.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

from .selectors import thumbnail_url, top_keywords


class LostItemListQuerySerializer(serializers.Serializer):
    found_date = serializers.DateField(required=False)
    page = serializers.IntegerField(required=False, min_value=0, default=0)
    size = serializers.IntegerField(
        required=False, min_value=1, max_value=MAX_PAGE_SIZE, default=DEFAULT_PAGE_SIZE
    )

# -------------------------------------------------------------------
# 등록(POST) 요청 검증
# -------------------------------------------------------------------

class LostItemCreateSerializer(serializers.Serializer):
    """분실물 등록(POST) 요청 바디 검증."""

    title = serializers.CharField(
        max_length=100,
        allow_blank=False,
        trim_whitespace=True,
    )

    found_date = serializers.DateField()

    image_urls = serializers.ListField(
        child=serializers.URLField(max_length=500),
        required=False,
        default=list,
    )

    tags = serializers.ListField(
        child=serializers.CharField(
            max_length=30,
            allow_blank=False,
            trim_whitespace=True,
        ),
        allow_empty=False,
    )

    def validate_found_date(self, value):
        """습득일은 축제 기간 안의 날짜만 허용."""
        start = settings.FESTIVAL_START_DATE
        end = settings.FESTIVAL_END_DATE

        if not (start <= value <= end):
            raise serializers.ValidationError(f"{start} ~ {end} 중에서 선택해주세요.")

        return value

    def validate_tags(self, value):
        """태그의 # 제거 및 중복 제거."""

        seen = set()
        deduplicated = []

        for keyword in value:
            # "#지갑", "##지갑" → "지갑"
            normalized = keyword.lstrip("#").strip()

            # 빈 문자열은 제외
            if not normalized:
                continue

            # 같은 태그가 이미 있으면 제외
            if normalized in seen:
                continue

            seen.add(normalized)
            deduplicated.append(normalized)

        if not deduplicated:
            raise serializers.ValidationError("키워드칩을 1개 이상 입력해주세요.")

        return deduplicated


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
    
    
class LostItemIdDataSerializer(serializers.Serializer):
    lost_item_id = serializers.IntegerField()


class LostItemIdResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    code = serializers.CharField(default="LOST_ITEM_CREATE_SUCCESS")
    message = serializers.CharField(default="분실물을 등록했습니다.")
    data = LostItemIdDataSerializer()