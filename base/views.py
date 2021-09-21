from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
''' Detailed descriptions, with full methods and attributes, for each of Django's class-based generic views. 
-->  http://ccbv.co.uk/  '''

from django.contrib.auth.views import LoginView  # login
from django.contrib.auth.mixins import LoginRequiredMixin  # for restriction... user can't do anything without login
from django.contrib.auth.forms import UserCreationForm  # for user registration
from django.contrib.auth import login  # for login we use login() here we use it after registration process

# Imports for Reordering Feature
from django.views import View
from django.shortcuts import redirect
from django.db import transaction

from .models import Task
from .forms import PositionForm


# login.... this is custom login class view we can use direct predefine login view like logout (logout -- check in  urls.py to understand )
# for more details about Built-in class-based views API ---  https://docs.djangoproject.com/en/3.1/ref/class-based-views/
class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    # here we are overriding success url to send tasks page
    def get_success_url(self):
        return reverse_lazy('tasks')


# register
# for read or understand  about FormView ---  http://ccbv.co.uk/projects/Django/3.1/django.views.generic.edit/FormView/
class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    # we are overriding from_valid(), to make suer requesting user is login user self
    def form_valid(self, form):
        user = form.save()  # save form values
        if user is not None:  # if user is created
            login(self.request, user)   # go to the user authenticated and logged in
        return super(RegisterPage, self).form_valid(form)

    # restrict or block authenticated user to go again to registration page without logout
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)


# display tasks list
# LoginRequiredMixin use for restriction... user can't do anything without login
''' Detailed descriptions, with full methods and attributes, for each of Django's class-based generic views. 
-->  http://ccbv.co.uk/  '''

class TaskList(LoginRequiredMixin, ListView):
    model = Task    # by using ListView  model is looking for (ModelName_list.html) task_list.html template
    context_object_name = 'tasks'     # by default queryset name 'object_list' here we customise our queryset name

    # get_context_data(), this returns back all our the data that we passing in
    # here we override get_context_data() so user only can access his own data
    # for more detail https://docs.djangoproject.com/en/3.1/ref/class-based-views/mixins-single-object/#django.views.generic.detail.SingleObjectMixin.get_context_data
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # we are inheriting from original data
        context['tasks'] = context['tasks'].filter(user=self.request.user)  # filtering to get to access self data
        context['count'] = context['tasks'].filter(complete=False).count()  # filtering to get uncompleted tasks

        # searching operation
        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(
                title__contains=search_input)

        context['search_input'] = search_input

        return context


# to view detail or information of task
class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task   # by using DetailView  model is looking for (ModelName_detail.html) task_detail.html template
    context_object_name = 'task'    # by default queryset name 'object' here we customise our queryset name
    template_name = 'base/task.html'   # here we customise name of template to task


# here we create task
class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task  # by using CreateView  model is looking for (ModelName_form.html) task_form.html template
    fields = ['title', 'description', 'complete']  # here we define fields which we want to display in form
    # reverse_lazy revers or send bake to tasks page after task created successful to set reverse_lazy we have use success_url attribute
    success_url = reverse_lazy('tasks')

    # we are overriding from_valid(), to make suer requesting user is login user self
    def form_valid(self, form):
        form.instance.user = self.request.user  # make suer requesting user is login user self
        return super(TaskCreate, self).form_valid(form)  # than continue with task creating from


# here we update tasks
class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task  # by using UpdateView  model is looking for (ModelName_form.html) task_form.html template
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')


class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task  # by using UpdateView  model is looking for (ModelName_confirm_delete.html) task_confirm_delete.html template
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')

    def get_queryset(self):
        owner = self.request.user
        return self.model.objects.filter(user=owner)


class TaskReorder(View):
    def post(self, request):
        form = PositionForm(request.POST)

        if form.is_valid():
            positionList = form.cleaned_data["position"].split(',')

            with transaction.atomic():
                self.request.user.set_task_order(positionList)

        return redirect(reverse_lazy('tasks'))
