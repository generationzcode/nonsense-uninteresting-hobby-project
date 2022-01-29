from . import views
from django.urls import path
urlpatterns = [path('', views.list,name="list"),path('view', views.view_products,name="view"),path('clear', views.clear,name="clear")]