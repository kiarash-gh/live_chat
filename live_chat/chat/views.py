from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Message,ChatRoom
from django.contrib.auth.models import User

@login_required
def room(request):
    messages = Message.objects.select_related('sender').all().order_by('-timestamp')[:50]
    return render(request, 'chat/room.html', {
        'username': request.user.username,
        'messages': reversed(messages) 
    })


@login_required
def chat_dashboard(request):
    chatrooms = request.user.chatrooms.all()
    return render(request, 'chat/dashboard.html', {'chatrooms': chatrooms})

@login_required
def create_chat(request):
    if request.method == 'POST':
        chat_type = request.POST.get('chat_type')
        user_ids = request.POST.getlist('users')  # selected users from form
        name = request.POST.get('name') if chat_type == 'group' else ""

        chat = ChatRoom.objects.create(chat_type=chat_type, name=name)
        chat.participants.add(request.user, *User.objects.filter(id__in=user_ids))
        return redirect('chatroom_detail', chat_id=chat.id)

    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/create_chat.html', {'users': users})


@login_required
def chatroom_detail(request, chat_id):
    chatroom = get_object_or_404(ChatRoom, id=chat_id)

    # Only allow users who are part of the chatroom
    if request.user not in chatroom.participants.all():
        return redirect('chat:chatroom_list')  # or show 403 page

    messages = Message.objects.filter(room=chatroom).order_by('timestamp')

    return render(request, 'chat/chatroom_detail.html', {
        'chatroom': chatroom,
        'messages': messages,
        'user': request.user,
    })

def login_view(request):
    if request.user.is_authenticated:
        return redirect('chat-dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('chat-dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('chat-dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after signing up
            return redirect('chat-dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')