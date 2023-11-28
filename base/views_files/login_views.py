from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.urls import reverse_lazy
import logging

logger = logging.getLogger(__name__)

class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        success_url = reverse_lazy('tasks')
        logger.info(f"Successful login. Redirecting to: {success_url}")
        return reverse_lazy('tasks')