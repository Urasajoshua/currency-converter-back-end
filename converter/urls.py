from django.urls import path
from . import views



urlpatterns = [
    path('',views.CurrencyList.as_view(),name='currency list'),
    path('<str:from_currency>/<str:to_currency>/<str:amount>',views.ConverterCurrency.as_view(),name='converter')
]