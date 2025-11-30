from django.http import JsonResponse
from django.views import View

class HomeView(View):
    def get(self, request):
        return JsonResponse({
            'message': 'Smart Task Analyzer API',
            'status': 'online',
            'endpoints': {
                'analyze': '/api/tasks/analyze/',
                'suggest': '/api/tasks/suggest/',
                'admin': '/admin/'
            }
        })
