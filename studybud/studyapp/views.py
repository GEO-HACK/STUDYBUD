from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm
# Create your views here.



def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method =='POST':
        username =request.POST.get('username').lower()#to compare it with the register username
        password =request.POST.get('password')

        try:
            user = User.objects.get(username= username)

        except:
            messages.error(request, 'user doesnt exsist!')

        user = authenticate(request, username =username , password = password)

        if user is not None:
           login(request, user)
           return redirect('home')
        
        else:
            messages.error(request, 'Username or password does not exist')



    context = {'page':page}#the dictionaty for the login page
    return render(request, 'studybud/login_register.html',context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
   
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)#using the post method of the form
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:#handles when there is an error.
            messages.error(request,'An error occured during registration!')
            return render(request, 'studybud/login_register.html',{'form':form})

    return render(request, 'studybud/login_register.html',{'form':form})



def home(request):
    q = request.GET.get('q') if request.GET.get ('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains = q)|
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )#GIVES all the rooms in the database

    topics = Topic.objects.all()

    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {
        'rooms':rooms,
        'topics':topics,
        'room_count':room_count,
        'room_messages':room_messages,
    }   
    return  render(request,'studybud/home.html',context)


def room(request,pk):
    room = Room.objects.get(id=pk)
    room_messages= room.message_set.all()
    participants = room.participants.all()  
    if request.method == 'POST':
        #method to creae a message
        room_messages = Message.objects.create(
            user= request.user,
            room=room,
            body= request.POST.get('body')

        )
        
        room.participants.add(request.user)
        return redirect('room',pk = room.id)
    context = {'room':room, 'room_messages':room_messages,'participants':participants   }        
    return render(request,'studybud/room.html',context)


def userProfile(request,pk):
    user = User.objects.get(id= pk)
    topics = Topic.objects.all()
    room_messages = user.message_set.all()
    rooms = user.room_set.all()
    context = {'user':user, 'rooms':rooms, 'topics':topics, 'room_messages':room_messages}
    return render(request,'studybud/profile.html',context)


@login_required(login_url='login')#prevent the user from acceessing the create button when they are not logged in.
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room=form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')#accessing the home page usong the name that was speciferd in the views page.

    context = {'form':form}
    return render(request, 'studybud/room_form.html',context)
@login_required(login_url='login')
def updateRoom(request , pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)#willl be prefilled wit the value
   
   
    if request.user != room.host :
        return HttpResponse('You are not a registerred client')
    
    
    if request.method == 'POST':
        form = RoomForm(request.POST,instance=room)#what room is being updated
        if form.is_valid():
            form.save()
            return redirect('home')#accessing the home page usong the name that was speciferd in the views page.

    context = {'form':form}
    return render(request, 'studybud/room_form.html',context)


@login_required(login_url='login')    

def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host :
        return HttpResponse('You are not a registerred client')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')#accessing the home page usong the name that was speciferd in the views page.

    return render(request, 'studybud/delete.html', {'obj':room})


@login_required(login_url='login')    
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user :
        return HttpResponse('You are not a registerred client')
    
    if request.method == 'POST':
        message.delete()
        return redirect('room',pk=message.room.id)#accessing the home page usong the name that was speciferd in the views page.
    return render(request, 'studybud/delete.html', {'obj':message})



