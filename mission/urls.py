
from django.urls import path
from mission.views import list_view, mission_form_view, update_mission_view, delete_mission_view, show_mission_view

urlpatterns = [ 
    path('', list_view, name="list_view"),
    path('new/', mission_form_view, name='mission_form_view'),
    path('edit/<int:mission_id>/', update_mission_view, name='edit_mission'),
    path('delete/<int:mission_id>/', delete_mission_view, name='delete_mission'),
    path('show/<int:mission_id>/', show_mission_view, name='show_mission'),
]