from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProductionPlanSerializer
from .process_production_plan import calculate_production_plan

class ProductionPlanView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ProductionPlanSerializer(data=request.data)
        if serializer.is_valid():
            load = serializer.validated_data['load']
            fuels = serializer.validated_data['fuels']
            powerplants = serializer.validated_data['powerplants']

            result = calculate_production_plan(load, fuels, powerplants)

            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
