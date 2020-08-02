from django.urls import include,path
from . import views
app_name = 'textRetrieval'
urlpatterns = [
    #search
    path('FullTextSearch/', views.FullTextSearch),
    path('FullTextSearch_Query/', views.FullTextSearch_Query),
    #simText rank
    path('sentsSearch/', views.sentsSearch),
    path('sentsSearch_Query/', views.sentsSearch_Query),
    #preprocess
    path('Preprocess/', views.Preprocess),
    path('Preprocess_Query/', views.Preprocess_Query),
    path('Preprocess_spimi_Query/', views.Preprocess_spimi_Query),
    #Zip Distribution
    path('ZipDistribution/', views.ZipDistribution),
    path('ZipDistribution_Query/', views.ZipDistribution_Query),

]