from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index.html', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('add-product/', views.add_product, name='add_product'),
    path('view-tracing/', views.view_tracing, name='view_tracing'),
    path('update-tracing/', views.update_tracing, name='update_tracing'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('admin-screen/', views.admin_screen, name='admin_screen'),
    path('user-screen/', views.user_screen, name='user_screen'),
]