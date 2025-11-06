from django.contrib import admin
from django.urls import path
from . import views 

urlpatterns = [

    path('', views.login_view, name='login_view'),  # Make login the root page
    path('logout/', views.logout_view, name='logout_view'),

    # --- NEW Election Dashboard ---
    path('elections/', views.election_list_view, name='election_list_view'),

    # --- NEW Dynamic Ballot Views ---
    # Example: /ballot/1/
    # This URL captures the '1' as 'election_id' and passes it to the view
    path('ballot/<int:election_id>/', views.ballot_view, name='ballot_view'),
    
    # Example: /cast-vote/1/
    # This URL handles the POST for a specific election
    path('cast-vote/<int:election_id>/', views.cast_ballot_view, name='cast_ballot_view'),

    # --- Status Pages ---
    path('thank-you/', views.thank_you_view, name='thank_you_view'),
    
    # (You would also add paths for your other status templates like 'ineligible.html')
    # path('ineligible/', views.ineligible_view, name='ineligible_view'), 
    # path('election-inactive/', views.election_inactive_view, name='election_inactive_view'),
]