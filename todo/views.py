from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request,'todo/home.html')

def signupuser(request):
    if request.method == 'GET':
        return render(request,'todo/signupuser.html',{'form': UserCreationForm()})
    else:
        #Create new user
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'],password=request.POST['password1'])
                user.save()
                login(request,user)
                return redirect('currenttodos')

            except IntegrityError:
                return render(request,'todo/signupuser.html',{'form': UserCreationForm(),'error':'Username already taken please choose new one'})

        else:
            return render(request,'todo/signupuser.html',{'form': UserCreationForm(),'error':'Passwords did not match'})
def loginuser(request):
    if request.method == 'GET':
        return render(request,'todo/loginuser.html',{'form': AuthenticationForm()})
    else:
        user = authenticate(request,username=request.POST['username'],password=request.POST['password'])
        if user is None:
            return render(request,'todo/loginuser.html',{'form': AuthenticationForm(), 'error':'username n password did not match'})
        else:
            login(request,user)
            return redirect('currenttodos')

@login_required           
def logoutuser(request):
    if request.method == "POST":
        logout(request)
        return redirect('home')

@login_required    
def createtodos(request):
    if request.method == 'GET':
        return render(request,'todo/createtodos.html',{'form': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.creator=request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request,'todo/createtodos.html',{'form': TodoForm(), 'error':'bad data passed in'})
            
@login_required    
def currenttodos(request):
    todos = Todo.objects.filter(creator=request.user, datecompleted__isnull=True)
    return render(request,'todo/currenttodos.html',{'todos':todos})


@login_required    
def completedtodos(request):
    todos = Todo.objects.filter(creator=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request,'todo/completedtodos.html',{'todos':todos})

@login_required    
def viewtodo(request, todo_pk):
    tlist = get_object_or_404(Todo, pk=todo_pk, creator=request.user) 
    if request.method == 'GET':
        form = TodoForm(instance=tlist)
        return render(request,'todo/detailtodo.html',{'tlist':tlist, 'form':form})
    else:
        try:
            form = TodoForm(request.POST, instance=tlist)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request,'todo/detailtodo.html',{'tlist':tlist, 'form':form, 'error':'Bad infor'})


@login_required    
def completetodo(request, todo_pk):
    tlist = get_object_or_404(Todo, pk=todo_pk, creator=request.user) 
    if request.method == 'POST':
        tlist.datecompleted = timezone.now()
        tlist.save()
        return redirect('currenttodos')


@login_required    
def deletetodo(request, todo_pk):
    tlist = get_object_or_404(Todo, pk=todo_pk, creator=request.user) 
    if request.method == 'POST':
        tlist.datecompleted = timezone.now()
        tlist.delete()
        return redirect('currenttodos')