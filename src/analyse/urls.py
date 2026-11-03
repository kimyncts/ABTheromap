from django.urls import path
from .views import nouvelle_analyse, afficher_chargement, resultats_analyse, telecharger_excel, detail_clone, telecharger_image, telecharger_excel_clone, supprimer_analyse


urlpatterns = [
    path('', nouvelle_analyse, name= "analyse-index"),
    path('chargement/<int:pk>/', afficher_chargement, name='afficher_chargement'),
    path('resultats/<int:pk>/', resultats_analyse, name='resultats_analyse'),
    path('resultats/<int:pk>/clone/<str:clone_id>/', detail_clone, name='detail_clone'),
    path('telecharger_excel/<int:pk>/', telecharger_excel, name='telecharger_excel'),
    path('telecharger_image/<int:pk>/<str:clone_id>/', telecharger_image, name='telecharger_image'),
    path('telecharger_excel_clone/<int:pk>/<str:type_clone>/<str:clone_id>/', telecharger_excel_clone, name='telecharger_excel_clone'),
    path('supprimer/<int:analyse_id>/', supprimer_analyse, name='supprimer_analyse'),
    
] 
