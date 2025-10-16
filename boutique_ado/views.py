from django.shortcuts import render


# Create your views here.

def handler404(request, exception):
    """Custom 404 Page Not Found"""
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    """Custom 500 Internal Server Error"""
    return render(request, 'errors/500.html', status=500)


def handler403(request, exception):
    """Custom 403 Permission Denied"""
    return render(request, 'errors/403.html', status=403)


def handler400(request, exception):
    """Custom 400 Bad Request"""
    return render(request, 'errors/400.html', status=400)
