from rest_framework import serializers
from .models import User,Workspace,Project,Task
from django.contrib.auth import authenticate

class UserSerializer(serializers.Serializer):
    class Meta:
        model=User
        fields=['id','name','email']



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
    
class WorkspaceSerializer(serializers.ModelSerializer):
        class Meta:
            model=Workspace
            fields=['id','name' ,'members']
            read_only_fields=['members']


class ProjectSerializers(serializers.ModelSerializer):
    members = serializers.StringRelatedField(many=True,read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'workspace', 'members']

   



class TaskSerializers(serializers.ModelSerializer):
    class Meta:
        model=Task
        fields=['id','project','title','description','assigned_to','deadline','created_at']

