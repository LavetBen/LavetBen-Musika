from django.urls import path
from . import views


urlpatterns = [
    path('login',views.login_view,name='login'),
    path('register',views.register,name='register'),
    path('',views.store,name='store'),
    path('home',views.home,name='home'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('view_cart',views.view_cart,name='view_cart'),
    path('quick_checkout', views.quick_checkout, name='quick_checkout'),
    path('logout',views.logout_view,name='logout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('remove_from_cart/<int:product_id>/',views.remove_from_cart,name='remove_from_cart')
    
   
]
