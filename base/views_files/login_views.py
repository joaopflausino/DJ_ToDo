from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
import logging

logger = logging.getLogger(__name__)


class CustomLoginView(LoginView):
    template_name = "base/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        logger.info("Successful login. Redirecting to tasks")
        return reverse_lazy("tasks")
