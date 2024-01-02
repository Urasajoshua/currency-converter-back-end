from rest_framework import generics
from .models import Currency ,updatedLog
from . import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import logging
from django.utils import timezone
from datetime import timedelta
import requests

logger = logging.getLogger(__name__)
UPDATE_INTERVAL = 1 #hours
EXCHANGE_RATE_API_URL = 'https://api.exchangerate-api.com/v4/latest/USD'

class CurrencyList(generics.ListAPIView):
    queryset = Currency.objects.all()
    serializer_class=serializers.CurrencySerializer
    
    
class ConverterCurrency(APIView):
    
    def get(self,request:Request,from_currency,to_currency,amount):
        try:
            self.update_rates_if_necessary()
            return self.perform_conversion(from_currency,to_currency,amount)
        except Exception as e:
            logger.error(str(e))
            return Response({"error":"unexpected errors"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def update_rates_if_necessary(self):
        try:
            last_updated=updatedLog.objects.latest('updated_at')
        except updatedLog.DoesNotExist:
            last_updated = None
            
        if not last_updated or last_updated.updated_at < timezone.now() - timedelta(hours=UPDATE_INTERVAL):
            self.update_rates()
            
    def update_rates(self):
        response = requests.get(EXCHANGE_RATE_API_URL)
        data =  response.json()
        
        if 'rates' not in data:
            raise Exception('could not fetch rates')
        
        for code, rate in data['rates'].items():
            Currency.objects.update_or_create(code=code,defaults={'rate':rate})
        updatedLog.objects.update_or_create(id=1,defaults={'updated_at':timezone.now})
        
    
    def perform_conversion(self,from_currency,to_currency,amount):
        try:
            from_rate = Currency.objects.get(code=from_currency.upper()).rate
            to_rate = Currency.objects.get(code=to_currency.upper()).rate
        except Currency.DoesNotExist:
            return Response(data={"error":"invalid currency"},status=status.HTTP_400_BAD_REQUEST)
        
        
        converted_amount = (float(amount)/from_rate) * to_rate
        return Response({'converted_amount':converted_amount},status=status.HTTP_200_OK)