from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from django.contrib.auth import login,logout,get_user_model
from .models import User,Workspace,Project,Task
from .serializers import SignupSerializer,LoginSerializer,WorkspaceSerializer,ProjectSerializers,TaskSerializers,UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework.decorators import api_view,permission_classes

# Create your views here.
#User=get_user_model
class SignupAPI(APIView):
    permission_classes=[permissions.AllowAny]
    def post(self,request):
        serializer=SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"User created sucessfully"},status=status.HTTP_201_CREATED)
        return Response({"error":"Email and password are required"},status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(APIView):
    permission_classes=[permissions.AllowAny]
    def post(self,request):
        serializer=LoginSerializer(data=request.data)
        if serializer.is_valid():
            user=serializer.validated_data['user']
            login(request,user)
            if user:

             refresh = RefreshToken.for_user(user)
            return Response({"message":"login sucess","refresh": str(refresh),
                "access": str(refresh.access_token)})
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class LogoutView(APIView):
    def post(self,request):
        try:
            refresh_token=request.data['refresh']
            token=RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail":"sucessfully logout"},status=200)
        except Exception:
            return Response({"error":"invalid token"},status=400)
    

class WorkspaceCreateAPI(APIView):
    def post(self,request):
        name=request.data.get("name")
        member_emails=request.data.get("members",[])

        if not name:
            return Response({"error":"Workspace name is requird"},status=status.HTTP_400_BAD_REQUEST)
        
        workspace=Workspace.objects.create(
        name=request.data.get("name"),
        created_by=request.user
        )
        workspace.members.add(request.user)

        if member_emails:
            users=User.objects.filter(email__in=member_emails)
            workspace.members.set(users)
        
        serializer=WorkspaceSerializer(workspace)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    


class WorkspaceUpdateAPI(APIView):
    def post(self,request,pk):
        try:
            workspace=Workspace.objects.get(pk=pk)
        except Workspace.DoesNotExist:
            return Response({"error":"Workspace not found"},status=status.HTTP_404_NOT_FOUND)
        
        name=request.data.get("name")
        member_emails=request.data.get("members",[])

        workspace.name=name
        workspace.save()

        if member_emails:
            users=User.objects.filter(email__in=member_emails)
            workspace.members.set(users)

        serializer=WorkspaceSerializer(workspace)
        return Response(serializer.data,status=status.HTTP_200_OK)
    

class WorkspaceMemberList(APIView):
    def get(self,request,workspace_id):
        workspace=get_object_or_404(Workspace,id=workspace_id)
        members=workspace.members.all()
        return Response([
            {"id":m.id,"name":m.name,"email":m.email}
            for m in members
        ],status=status.HTTP_200_OK)
    

class ProjectCreateAPI(APIView):
    def post(self,request):
        name=request.data.get('name')
        description=request.data.get('description','')
        workspace_id=request.data.get('workspace')
        member_ids=request.data.get('members',[])

        if not name or not workspace_id:
            return Response({"error":"Project name and workspace required"})
        

        workspace=get_object_or_404(Workspace,id=workspace_id)

        workspace_members_ids= set(workspace.members.values_list('id', flat=True))

        project=Project.objects.create(name=name,description=description,workspace=workspace)

        valid_members=User.objects.filter(id__in=member_ids)
        project.members.set(valid_members)
        serializer=ProjectSerializers(project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)




class TaskCreateAPI(APIView):
    def post(self, request):
        serializer = TaskSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Task created successfully", "task": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    





class CurrentUserAPI(APIView):
    permission_classes = [IsAuthenticated]   
    
    def get(self, request):
        serializer = UserSerializer(request.user)    
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UpdateProfileInfo(APIView):
    permission_classes=[IsAuthenticated]
    def patch(self,request):
        serializer=UserSerializer(request.user,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_workspacelist(request):
    workspaces=Workspace.objects.filter(members=request.user)
    serializer=WorkspaceSerializer(workspaces,many=True)
    return Response(serializer.data,status=status.HTTP_200_OK)


@api_view(['GET','DELETE'])
@permission_classes([IsAuthenticated])
def workspace_details(request,pk):
    if request.method=='GET':
        workspace=get_object_or_404(Workspace,id=pk,members=request.user)
        serializer=WorkspaceSerializer(workspace)
        return Response(serializer.data)
    
    elif request.method=='DELETE':
        workspace=get_object_or_404(Workspace,id=pk)
        if workspace.created_by != request.user:
            return Response({"error":"only owner can delete the workspace"},status=status.HTTP_403_FORBIDDEN)
        workspace.delete()
        return Response({"detail": "Workspace deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_members(request,pk):
    workspace=get_object_or_404(Workspace,id=pk)
    if workspace.created_by != request.user:
        return Response({"error":"only admin can add users"},status=status.HTTP_403_FORBIDDEN)
    
    email=request.data.get("email")
    if not email:
        return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

    workspace.members.add(user)
    return Response({"detail": f"{user.email} added to workspace"}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_member(request,pk,user_id):
    workspace=get_object_or_404(Workspace,id=pk)
    if workspace.created_by != request.user:
        return Response({"error":"only admin can delete users"},status=status.HTTP_403_FORBIDDEN)
    
    try:
        user=User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
    
    workspace.members.remove(user)
    return Response({"detail": f"{user.email} removed from workspace"}, status=status.HTTP_200_OK)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def project_list(request):
    workspace_id = request.query_params.get("workspace")
    if not workspace_id:
        return Response({"error": "workspace id required"}, status=status.HTTP_400_BAD_REQUEST)

    workspace = get_object_or_404(Workspace, id=workspace_id)
    if request.user not in workspace.members.all():
        return Response({"error": "Not a member of this workspace"}, status=status.HTTP_403_FORBIDDEN)

    projects = Project.objects.filter(workspace=workspace)
    serializer = ProjectSerializers(projects, many=True)
    return Response(serializer.data)


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def project_detail(request, id):
    project = get_object_or_404(Project, id=id)

    if request.user not in project.workspace.members.all():
        return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        serializer = ProjectSerializers(project)
        return Response(serializer.data)

    elif request.method == "PATCH":
        serializer = ProjectSerializers(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        project.delete()
        return Response({"message": "Project deleted successfully"}, status=status.HTTP_204_NO_CONTENT)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_project_member(request, id):
    project = get_object_or_404(Project, id=id)
    if request.user not in project.workspace.members.all():
        return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

    user_id = request.data.get("user_id")
    user = get_object_or_404(User, id=user_id)

    if user not in project.workspace.members.all():
        return Response({"error": "User not part of workspace"}, status=status.HTTP_400_BAD_REQUEST)

    project.members.add(user)
    return Response({"message": "Member added successfully"})



@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_project_member(request, id, user_id):
    project = get_object_or_404(Project, id=id)
    if request.user not in project.workspace.members.all():
        return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

    user = get_object_or_404(User, id=user_id)
    if user in project.members.all():
        project.members.remove(user)
        return Response({"message": "Member removed successfully"})
    return Response({"error": "User not in project"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_list(request):
    project_id=request.query_param.get("project")
    if not project_id:
        return Response({"error":"project id required"},status=status.HTTP_400_BAD_REQUEST)
    project=get_object_or_404(Project,id=project_id)
    if request.user not in project.members.all():
        return Response({"error":"not allowed"},status=status.HTTP_403_FORBIDDEN)
    tasks=Task.objects.filter(project=project)
    serializer=TaskSerializers(tasks,many=True)
    return Response(serializer.data)


@api_view(['GET','PATCH','DELETE'])
@permission_classes([IsAuthenticated])
def task_detail(request,id):
    task=get_object_or_404(Task,id=id)
    if request.user not in task.project.members.all():
        return Response({"error":"not allowed"},status=status.HTTP_403_FORBIDDEN)
    
    if request.method=='GET':
        serializer=TaskSerializers(task)
        return Response(serializer.data)
    
    elif request.method=='PATCH':
        serializer=TaskSerializers(task,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.save)
        return Response(serializer.error,status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method=='DELETE':
        task.delete()
        return Response({"message": "Task deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def assign_task(request, id):
    task = get_object_or_404(Task, id=id)
    if request.user not in task.project.members.all():
        return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

    user_id = request.data.get("user_id")
    if not user_id:
        return Response({"error": "user_id required"}, status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(User, id=user_id)

    if user not in task.project.members.all():
        return Response({"error": "User not in project"}, status=status.HTTP_400_BAD_REQUEST)

    task.assignee = user
    task.save()
    return Response({"message": "Task assigned successfully"})


# Update task status
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_task_status(request, id):
    task = get_object_or_404(Task, id=id)
    if request.user not in task.project.members.all():
        return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

    status_value = request.data.get("status")
    if status_value not in ["To Do", "In Progress", "Done"]:
        return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

    task.status = status_value
    task.save()
    return Response({"message": "Status updated successfully"})