from django.contrib import admin
from django.urls import path
from pages import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Public
    path('', views.home, name='home'),
    path('grid/', views.grid_demo, name='grid_demo'),

    # Auth
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # @login_required
    path('dashboard/', views.dashboard, name='dashboard'),
    path('article/new/', views.create_article, name='create_article'),
    path('article/<int:pk>/edit/', views.edit_article, name='edit_article'),

    # @permission_required
    path('article/<int:pk>/delete/', views.delete_article, name='delete_article'),

    # @user_passes_test (superuser only)
    path('admin-only/', views.admin_only_page, name='admin_only'),

    # @staff_member_required
    path('staff/', views.staff_panel, name='staff_panel'),

    # Stacked decorators (@login_required + @require_POST)
    path('quick-publish/', views.quick_publish, name='quick_publish'),
]
