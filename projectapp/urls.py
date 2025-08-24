from django.urls import path
from .views import *

urlpatterns = [
    path('signup/',SignupAPI.as_view(),name='signup'),
    path('login/',LoginView.as_view(),name='login'),
    path('workspacecreate/',WorkspaceCreateAPI.as_view(),name='workspacecreate'),
    path('workspaceupdate/<int:pk>/',WorkspaceUpdateAPI.as_view(),name='workspaceupdate'),
    path('workspace_members/<int:workspace_id>/',WorkspaceMemberList.as_view(),name='workspace_member'),

    path('projectcreate/',ProjectCreateAPI.as_view(),name='projectcreate'),
     path('taskcreate/', TaskCreateAPI.as_view(),name='taskcreate'),

]





