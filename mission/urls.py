
from django.urls import path
from mission.views.list_views import list_view, show_mission_view, list_interventions_view
from mission.views.form_views import get_mission_form_view, post_mission_form_view, get_update_mission_view, post_update_mission_view, delete_mission_view, create_intervention_view, update_intervention_view, delete_intervention_view


urlpatterns = [ 
    path('', list_view, name="list_view"),
    path('new/', get_mission_form_view, name='get_mission_form_view'),
    path('new/post', post_mission_form_view, name='post_mission_form_view'),
    path('edit/<int:mission_id>/', get_update_mission_view, name='edit_mission'),
    path('edit/<int:mission_id>/post', post_update_mission_view, name='post_update_mission'),
    path('delete/<int:mission_id>/', delete_mission_view, name='delete_mission'),
    path('show/<int:mission_id>/', show_mission_view, name='show_mission'),
    path('intervention/', list_interventions_view, name='list_interventions_view'),
    path('intervention/edit/<int:intervention_id>/', update_intervention_view, name='edit_intervention'),
    path('intervention/delete/<int:intervention_id>/', delete_intervention_view, name='delete_intervention'),
    path('intervention/new/', create_intervention_view, name='create_intervention')
]