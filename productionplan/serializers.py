from rest_framework import serializers

class ProductionPlanSerializer(serializers.Serializer):
    load = serializers.FloatField()
    fuels = serializers.DictField()
    powerplants = serializers.ListField()
