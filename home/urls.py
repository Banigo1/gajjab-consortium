
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('about-us', views.about_view, name='about'),
    path('services', views.services_view, name='services'),
    path('team', views.team_view, name='our-team'),
    path('contact', views.contact_view, name='contact'),
    path('move-cargo', views.move_cargo, name='move_cargo'),
    path('features', views.features_view, name='features'),
    path('faq', views.faq_view, name='faq'),
    path('track', views.track_view, name='track'),
    path('Dashboard', views.track_widget, name='Security_Widget'),
    path('location', views.location_view, name='location'),
]