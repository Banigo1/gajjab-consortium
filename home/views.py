from django.shortcuts import render

def index_view(request):
    return render(request, 'index.html', context={'title': 'Home'})

def about_view(request):
    return render(request, 'about-us.html', context={'title': 'About Us'})

def services_view(request):
    return render(request, 'services.html', context={'title': 'Services'})

def team_view(request):
    return render(request, 'team.html', context={'title': 'Our Team'})

def contact_view(request):
    return render(request, 'contact.html', context={'title': 'Contact Us'})

def move_cargo(request):
    return render(request, 'move-cargo.html', context={'title': 'Move Cargo'})

def features_view(request):
    return render(request, 'features.html', context={'title': 'Features'})

def track_view(request):
    return render(request, 'track.html', context={'title': 'Track and Trace'})

def track_widget(request):
    return render(request, 'SecurityWidget.html', context={'title': 'Dashboard'})

def location_view(request):
    return render(request, 'location.html', context={'title': 'Location'})

def faq_view(request):
    return render(request, 'faqs.html', context={'title': 'FAQs'})


