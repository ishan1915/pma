from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from django.contrib.auth import login
from .models import User,Workspace,Project,Task
from .serializers import SignupSerializer,LoginSerializer,WorkspaceSerializer,ProjectSerializers,TaskSerializers
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.

class SignupAPI(APIView):
    permission_classes=[permissions.AllowAny]
    def post(self,request):
        serializer=SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"User created sucessfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_404_NOT_FOUND)
    

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
    

class WorkspaceCreateAPI(APIView):
    def post(self,request):
        name=request.data.get("name")
        member_emails=request.data.get("members",[])

        if not name:
            return Response({"error":"Workspace name is requird"},status=status.HTTP_400_BAD_REQUEST)
        
        workspace=Workspace.objects.create(name=name)

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