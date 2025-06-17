from django.urls import path
from ecommerceapp import views

urlpatterns = [
    path('', views.index, name="index"),
    path('contact', views.contact, name="contact"),
    path('about', views.about, name="about"),
    path('profile', views.profile, name="profile"),
    path('checkout/', views.checkout, name="checkout"),
    path('handlerequest/', views.handlerequest, name="handlerequest"),

    # Modify the add_to_cart route to accept a product ID
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name="add_to_cart"),

    # Added search route
    path('search/', views.search_products, name="search"),
]
