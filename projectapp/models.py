from django.db import models
 
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
 
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']  # only name is required in createsuperuser

    def __str__(self):
        return self.email

    

class Workspace(models.Model):
    name=models.CharField(max_length=255)
    members=models.ManyToManyField(User,related_name="workspaces")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_workspaces")  # 👈 add this



    def __str__(self):
        return self.name
    


class Project(models.Model):
    workspace=models.ForeignKey(Workspace,on_delete=models.CASCADE,related_name="tasks")
    name=models.CharField(max_length=20)
    description=models.TextField(blank=True,null=True)
    members=models.ManyToManyField(User,related_name="projects")

    def __str__(self):
        return self.name
    


class Task(models.Model):
    project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name="tasks")
    title=models.CharField(max_length=255)
    description=models.TextField(blank=True,null=True)
    assigned_to=models.ForeignKey(User,on_delete=models.CASCADE,related_name="tasks")
    deadline=models.DateField()
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
