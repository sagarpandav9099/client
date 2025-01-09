from django.contrib import admin
from django.urls import path, include
from client_app.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='home'),
    path('client/', include('client_app.urls')),  # Our client app routes
]
