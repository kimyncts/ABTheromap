from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from analyse.models import Analysis

# Create your views here.
def index (request):
    return render(request, "accounts/index.html")

def login_user(request):
    if request.method == 'POST' :
        username = request.POST["username"]
        password = request.POST["password"]
        
        user = authenticate(request, username = username, password = password)
        
        if user is not None :
            login(request,user)
            return redirect ('index')
        else : 
            messages.info(request, "Identifiant et/ou mot de passe incorrect")
    form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})

def logout_user(request):
    logout(request)
    return redirect('index')

def signup_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})


def historique_user(request):
    analyses = Analysis.objects.filter(user=request.user).order_by('-start_time')
    return render(request, 'accounts/historique.html', {'analyses': analyses})


def confirmation_logout (request):
    return render(request, "accounts/confirmation.html")
