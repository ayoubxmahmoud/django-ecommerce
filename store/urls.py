from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),
    path('profile/<int:pk>', views.userProfile, name="user-profile"),
    path('update-user/', views.updateUser, name="update-user"),
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.updateItem, name="updateItem"),
    path('proccess_order/', views.proccessOrder, name="proccess-order"),
    path('show/<int:product_id>/', views.displayProduct, name="display-product"),

]


