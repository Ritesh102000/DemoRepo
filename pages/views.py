"""
=============================================================
  Lecture 5 — Django Decorators & Bootstrap Grid System
=============================================================
This file demonstrates the most common Django view decorators
and how they protect your views.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import (
    login_required,          # ← user must be logged in
    permission_required,     # ← user must have a specific permission
    user_passes_test,        # ← user must pass a custom test
)
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse

from .forms import SignUpForm, ArticleForm
from .models import Article


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  1. PUBLIC VIEWS  (no decorator — anyone can access)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def home(request):
    """Home page — also demonstrates Bootstrap Grid system."""
    articles = Article.objects.all().order_by('-created_at')
    return render(request, 'home.html', {'articles': articles})


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    from django.contrib.auth.forms import AuthenticationForm
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            # Redirect to 'next' param if present (set by @login_required)
            return redirect(request.GET.get('next', 'dashboard'))
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  2. @login_required  — must be logged in
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  If user is NOT logged in → redirects to LOGIN_URL (settings.py)
#  The original URL is passed as ?next= so user comes back after login.

@login_required
def dashboard(request):
    """Only logged-in users can see their dashboard."""
    my_articles = Article.objects.filter(author=request.user)
    return render(request, 'dashboard.html', {'articles': my_articles})


@login_required
def create_article(request):
    """Only logged-in users can write articles."""
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect('dashboard')
    else:
        form = ArticleForm()
    return render(request, 'create_article.html', {'form': form})


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  3. @user_passes_test  — custom condition
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Pass any function that takes a User and returns True/False.
#  If False → redirects to LOGIN_URL.

def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def admin_only_page(request):
    """Only superusers can access this page."""
    return render(request, 'admin_only.html')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  4. @permission_required  — Django permission system
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Checks if user has a specific permission (from the Permission model).
#  Permissions are auto-created for every model: add, change, delete, view.
#  Format: 'app_label.codename'  e.g. 'pages.delete_article'

@permission_required('pages.delete_article', raise_exception=True)
def delete_article(request, pk):
    """Only users with 'pages.delete_article' permission can delete."""
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        article.delete()
        return redirect('dashboard')
    return render(request, 'confirm_delete.html', {'article': article})


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  5. @staff_member_required  — is_staff must be True
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  From django.contrib.admin.views.decorators
#  Checks user.is_active and user.is_staff

@staff_member_required
def staff_panel(request):
    """Only staff members (is_staff=True) can see this."""
    all_articles = Article.objects.all().order_by('-created_at')
    return render(request, 'staff_panel.html', {'articles': all_articles})


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  6. @require_http_methods / @require_POST  — restrict HTTP methods
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Returns 405 Method Not Allowed if wrong method is used.

@login_required
@require_http_methods(["GET", "POST"])
def edit_article(request, pk):
    """Only GET and POST allowed (no PUT, DELETE, etc.)."""
    article = get_object_or_404(Article, pk=pk, author=request.user)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ArticleForm(instance=article)
    return render(request, 'edit_article.html', {'form': form, 'article': article})


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  7. STACKING DECORATORS  — combine multiple decorators
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Decorators are applied bottom-up:
#    1. First @require_POST checks HTTP method
#    2. Then @login_required checks authentication

@login_required
@require_POST
def quick_publish(request):
    """POST-only + must be logged in. Demonstrates stacking decorators."""
    title = request.POST.get('title', 'Untitled')
    Article.objects.create(title=title, body='Quick post!', author=request.user)
    return redirect('dashboard')


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GRID DEMO PAGE — dedicated page to teach Bootstrap Grid
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def grid_demo(request):
    """Standalone page showing Bootstrap grid examples."""
    return render(request, 'grid_demo.html')
