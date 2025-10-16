from django.shortcuts import render


# Create your views here.
def handler404(request, exception):
    """ 404 error handler """
    return render(request, 'errors/404.html', status=404)
