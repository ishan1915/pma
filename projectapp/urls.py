from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('signup/',SignupAPI.as_view(),name='signup'),
    path('login/',LoginView.as_view(),name='login'),
    path('logout/',LogoutView.as_view(),name='logout'),

    path('user/profile/',CurrentUserAPI.as_view(),name='user_profile'),
    path('user/update/',UpdateProfileInfo.as_view(),name='update_profile'),


    path('workspaces/',user_workspacelist,name='workspacelist'),
    path('workspace/<int:pk>/',workspace_details,name='workspace_details'),

    path("workspace/<int:pk>/add_member/",  add_members, name="workspace-add-member"),
    path("workspace/<int:pk>/remove_member/<int:user_id>/", remove_member, name="workspace-remove-member"),




    path('workspacecreate/',WorkspaceCreateAPI.as_view(),name='workspacecreate'),
    path('workspaceupdate/<int:pk>/',WorkspaceUpdateAPI.as_view(),name='workspaceupdate'),
    path('workspace_members/<int:workspace_id>/',WorkspaceMemberList.as_view(),name='workspace_member'),

    path('projectcreate/',ProjectCreateAPI.as_view(),name='projectcreate'),
    path('taskcreate/', TaskCreateAPI.as_view(),name='taskcreate'),

    path("projects/", project_list, name="project-list"),
    path("project/<int:id>/", project_detail, name="project-detail"),
    path("project/<int:id>/add_member/", add_project_member, name="project-add-member"),

    path("project/<int:id>/new_add_member/", add_new_usertoproject , name="project-add-member-new"),
    path("project/<int:id>/remove_member/<int:user_id>/", remove_project_member, name="project-remove-member"),


    path("tasks/", task_list, name="task-list"),
    path("task/<int:id>/", task_detail, name="task-detail"),
    path("task/<int:id>/assign/", assign_task, name="assign-task"),
    path("task/<int:id>/status/", update_task_status, name="task-status"),


     path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     path('token/obtain/',TokenObtainPairView.as_view(),name='token_obtain'),


]





