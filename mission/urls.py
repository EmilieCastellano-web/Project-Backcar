
from django.urls import path
from mission.views import list_view, mission_form_view, update_mission_view

urlpatterns = [ 
    path('', list_view, name="list_view"),
    path('new/', mission_form_view, name='post_mission'),
    path('edit/<int:mission_id>/', update_mission_view, name='edit_mission')
]