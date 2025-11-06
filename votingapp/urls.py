from django.contrib import admin
from django.urls import path
from . import views 

urlpatterns = [
    # path('admin/', admin.site.urls),

    # --- Authentication ---
    path('', views.login_view, name='login_view'),
    
    path('logout/', views.logout_view, name='logout_view'),


    # --- Voting Flow ---
    path('elections/', views.election_list_view, name='election_list_view'),
    
    path('ballot/<int:election_id>/', views.ballot_view, name='ballot_view'),
    
    path('cast-vote/<int:election_id>/', views.cast_ballot_view, name='cast_ballot_view'),
    
    path('thank-you/', views.thank_you_view, name='thank_you_view'),


    # --- ADMIN RESULTS URLS ---
    path('results/', views.results_dashboard_view, name='results_dashboard'),
    
    path('results/<int:election_id>/', views.election_results_view, name='election_results'),

]