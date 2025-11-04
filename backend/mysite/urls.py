"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings


def api_root(request):
    """API root endpoint with available endpoints information."""
    return JsonResponse({
        'message': 'Welcome to the Cats API!',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'api': {
                'cats': '/api/cats/',
                'cats_available': '/api/cats/available/',
                'cats_adopted': '/api/cats/adopted/',
                'cats_statistics': '/api/cats/statistics/',
                'cats_breeds': '/api/cats/breeds/',
                'cats_search': '/api/cats/search/',
            },
            'browsable_api': '/api/cats/',
        },
        'documentation': {
            'endpoints_help': {
                'GET /api/cats/': 'List all cats with pagination and filtering',
                'GET /api/cats/{id}/': 'Get details of a specific cat',
                'POST /api/cats/': 'Create a new cat record',
                'PUT/PATCH /api/cats/{id}/': 'Update cat information',
                'DELETE /api/cats/{id}/': 'Delete a cat record',
                'POST /api/cats/{id}/adopt/': 'Adopt a cat',
                'POST /api/cats/{id}/return_to_shelter/': 'Return cat to shelter',
                'GET /api/cats/available/': 'List available cats for adoption',
                'GET /api/cats/adopted/': 'List adopted cats',
                'GET /api/cats/statistics/': 'Get comprehensive statistics',
                'GET /api/cats/breeds/': 'Get breed statistics',
                'GET /api/cats/search/': 'Advanced search with multiple criteria',
            },
            'query_parameters': {
                'status': 'Filter by adoption status (available/adopted)',
                'breed': 'Filter by breed name (partial match)',
                'neutered': 'Filter by neutered status (true/false)',
                'min_age': 'Filter by minimum age',
                'max_age': 'Filter by maximum age',
                'search': 'Search in name, breed, color, description',
                'ordering': 'Order by field (id, name, age, weight, created_at)',
                'page': 'Page number for pagination',
            }
        },
        'server_info': {
            'debug_mode': settings.DEBUG,
            'django_version': '5.2',
            'python_version': '3.14.0',
        }
    })


urlpatterns = [
    # Admin interface
    path("admin/", admin.site.urls),
    
    # API root
    path('api/', api_root, name='api_root'),
    
    # Cats API
    path('', include('cats.urls')),
    
    # Django REST Framework browsable API
    path('api-auth/', include('rest_framework.urls')),
]
