from django.urls import path

from server.attacks import views

urlpatterns = [
    path('instances', views.InstanceListView.as_view(), name='instance-list'),
    path('start-test', views.AttackStartView.as_view(), name='attack-start'),
    # todo: list-tests
]
