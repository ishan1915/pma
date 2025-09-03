from rest_framework import serializers
from .models import User,Workspace,Project,Task
from django.contrib.auth import authenticate,get_user_model


#User=get_user_model

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','name','email']
        extra_kwargs = {"password": {"write_only": True}}


class AddUserSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True)
    confirm_password=serializers.CharField(write_only=True)

    class Meta:
        model=User
        fields=['name','email','skills','experience','phone','password','confirm_password']

    def validate(self,data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("password do not match")
        return data
    
    def create(self,validate_data):
        validate_data.pop('confirm_password')
        user=User.objects.create_user(**validate_data)
        return user

class SignupSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True)
    confirm_password=serializers.CharField(write_only=True)

    class Meta:
        model=User
        fields=['name','email','password','confirm_password']

    def validate(self,data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("password do not match")
        return data
    
    def create(self,validate_data):
        validate_data.pop('confirm_password')
        user=User.objects.create_user(**validate_data)
        return user
    

class LoginSerializer(serializers.Serializer):
    email=serializers.EmailField()
    password=serializers.CharField()

    def validate(self,data):
        user=authenticate(email=data['email'],password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        return {'user':user}
    

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "email"]

class WorkspaceSerializer(serializers.ModelSerializer):
    members = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="email"
    )

    class Meta:
        model = Workspace
        fields = ['id', 'name', 'members']


class ProjectSerializers(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)   
    workspace = serializers.StringRelatedField()           

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'workspace', 'members']


   


class TaskSerializers(serializers.ModelSerializer):
    assignee = UserMiniSerializer(source="assigned_to", read_only=True)  
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="assigned_to",  
        write_only=True,
        required=False
    )

    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all()
    )

    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "status", "deadline",
            "project", "assignee", "assignee_id", "created_at"
        ]
