"""Booths request and response serializers."""

from rest_framework import serializers


# 장소 목록 카드. BoothOperation 행을 입력으로 받는다 (부스당 최대 1행)
class BoothListItemSerializer(serializers.Serializer):
    booth_id = serializers.IntegerField(source="booth.id")
    name = serializers.CharField(source="booth.name")
    subtitle = serializers.CharField(source="booth.subtitle")
    place_type = serializers.CharField(source="booth.place_type")
    category = serializers.CharField(source="booth.category")
    location_detail = serializers.CharField(source="booth.location_detail")
    directions = serializers.CharField(source="booth.directions")
    zone = serializers.CharField(source="booth.zone")
    map_x = serializers.FloatField(source="booth.map_x")
    map_y = serializers.FloatField(source="booth.map_y")
    map_elevation = serializers.FloatField(source="booth.map_elevation")
    rotation = serializers.FloatField(source="booth.rotation")
    thumbnail_url = serializers.CharField(source="booth.thumbnail_url")
    lantern_count = serializers.IntegerField(source="booth.lantern_count")
    has_my_lantern = serializers.SerializerMethodField()
    operation = serializers.SerializerMethodField()

    def get_has_my_lantern(self, obj):
        # TODO: 등불(Lantern) 모델 머지 후 로그인 사용자의 등불 보유 여부로 대체
        return False

    def get_operation(self, obj):
        return {
            "open_at": obj.open_at.strftime("%H:%M"),
            "close_at": obj.close_at.strftime("%H:%M"),
        }
