from django.urls import include, path

urlpatterns = [
    path('tests/', include('server.attacks.urls')),
]
