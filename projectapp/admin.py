from django.contrib import admin
from .models import User,UserManager,Task,Workspace,Project
# Register your models here.
admin.site.register(User)
admin.site.register(Workspace)
admin.site.register(Project)
admin.site.register(Task)
 