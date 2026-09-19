"""공연 API 요청/응답 데이터 처리.

- 조회 조건 검증
- 응답 데이터 변환 및 Swagger 스키마 정의
"""

from django.conf import settings
from rest_framework import serializers


class PerformanceListQuerySerializer(serializers.Serializer):
    """타임테이블 조회 조건 검증."""

    date = serializers.DateField(required=False)

    def validate_date(self, value):
        # 축제 기간(9/29~10/1) 밖의 날짜면 막는다.
        start, end = settings.FESTIVAL_START_DATE, settings.FESTIVAL_END_DATE
        if not (start <= value <= end):
            raise serializers.ValidationError(f"{start} ~ {end} 중에서 선택해주세요.")
        return value


def to_list_item(performance, *, is_live):
    """타임테이블 카드 한 장으로 변환한다."""
    return {
        "performance_id": performance.pk,
        "team_name": performance.team_name,
        "affiliation": performance.affiliation,
        "image_url": performance.image_url,
        "start_at": performance.start_at,
        "end_at": performance.end_at,
        "is_live": is_live,
    }


def to_detail(performance):
    """상세 화면용으로 변환한다. 셋리스트는 sort_order 순서 그대로."""
    return {
        "performance_id": performance.pk,
        "team_name": performance.team_name,
        "affiliation": performance.affiliation,
        "description": performance.description,
        "image_url": performance.image_url,
        "festival_date": performance.festival_date,
        "start_at": performance.start_at,
        "end_at": performance.end_at,
        "songs": [
            {
                "song_id": song.pk,
                "title": song.title,
                "artist": song.artist,
                "sort_order": song.sort_order,
            }
            for song in performance.alive_songs
        ],
    }


# --- 응답 스키마 (Swagger 문서 전용) -------------------------------------------


class PerformanceListItemSerializer(serializers.Serializer):
    performance_id = serializers.IntegerField()
    team_name = serializers.CharField()
    affiliation = serializers.CharField(allow_null=True)
    image_url = serializers.URLField(allow_null=True)
    start_at = serializers.DateTimeField()
    end_at = serializers.DateTimeField()
    is_live = serializers.BooleanField()


class PerformanceListDataSerializer(serializers.Serializer):
    festival_date = serializers.DateField()
    server_time = serializers.DateTimeField()
    performances = PerformanceListItemSerializer(many=True)


class PerformanceListResponseSerializer(serializers.Serializer):
    """공연 타임테이블 조회 성공 응답."""

    success = serializers.BooleanField(default=True)
    code = serializers.CharField(default="PERFORMANCE_LIST_SUCCESS")
    message = serializers.CharField(default="공연 목록을 조회했습니다.")
    data = PerformanceListDataSerializer()


class SongSerializer(serializers.Serializer):
    song_id = serializers.IntegerField()
    title = serializers.CharField()
    artist = serializers.CharField(allow_null=True)
    sort_order = serializers.IntegerField()


class PerformanceDetailDataSerializer(serializers.Serializer):
    performance_id = serializers.IntegerField()
    team_name = serializers.CharField()
    affiliation = serializers.CharField(allow_null=True)
    description = serializers.CharField(allow_null=True)
    image_url = serializers.URLField(allow_null=True)
    festival_date = serializers.DateField()
    start_at = serializers.DateTimeField()
    end_at = serializers.DateTimeField()
    songs = SongSerializer(many=True)


class PerformanceDetailResponseSerializer(serializers.Serializer):
    """공연 상세 조회 성공 응답."""

    success = serializers.BooleanField(default=True)
    code = serializers.CharField(default="PERFORMANCE_DETAIL_SUCCESS")
    message = serializers.CharField(default="공연 정보를 조회했습니다.")
    data = PerformanceDetailDataSerializer()


class PerformanceNowDataSerializer(serializers.Serializer):
    server_time = serializers.DateTimeField()
    performances = PerformanceListItemSerializer(many=True)


class PerformanceNowResponseSerializer(serializers.Serializer):
    """지금 공연 중 조회 성공 응답."""

    success = serializers.BooleanField(default=True)
    code = serializers.CharField(default="PERFORMANCE_NOW_SUCCESS")
    message = serializers.CharField(default="현재 공연 정보를 조회했습니다.")
    data = PerformanceNowDataSerializer()