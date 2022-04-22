from . import views
from django.urls import path
urlpatterns = [path('', views.list,name="list"),path('view', views.view_products,name="view"),path('clear', views.clear,name="clear"),path('alt', views.list2,name="list_alt"),path('view_alt', views.view_tally,name="view_alt")]