# task_views.py
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.views import View
from django.shortcuts import redirect
from django.db import transaction
import logging

from ..models import Task
from ..forms import PositionForm

logger = logging.getLogger(__name__)


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = "tasks"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks"] = context["tasks"].filter(user=self.request.user)
        context["count"] = context["tasks"].filter(complete=False).count()
        search_input = self.request.GET.get("search-area") or ""
        if search_input:
            context["tasks"] = context["tasks"].filter(title__contains=search_input)

        context["search_input"] = search_input

        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = "task"
    template_name = "base/task.html"

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ["title", "description", "complete"]
    success_url = reverse_lazy("tasks")

    def form_valid(self, form):
        form.instance.user = self.request.user
        cache_key = f"task_form_{self.request.user.id}"
        cached_data = cache.get(cache_key, [])
        cached_data.append(form.cleaned_data)
        cache.set(cache_key, cached_data, timeout=None)

        logger.info(
            f"Task created: {form.instance.title} by {self.request.user.username}"
        )

        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ["title", "description", "complete"]
    success_url = reverse_lazy("tasks")

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = "task"
    success_url = reverse_lazy("tasks")

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class TaskReorder(View):
    def post(self, request):
        form = PositionForm(request.POST)
        if form.is_valid():
            position_ids = form.cleaned_data["position"].split(",")

            with transaction.atomic():
                for idx, task_id in enumerate(position_ids):
                    Task.objects.filter(id=int(task_id), user=request.user).update(
                        _order=idx
                    )

        return redirect(reverse_lazy("tasks"))
