from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView

from .models import Employee


class UserLoginView(View):
    template_name = "core/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("employees")
        return render(request, self.template_name)

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("employees")
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )
        if user is not None:
            login(request, user)
            request.session["user_id"] = user.id
            request.session["username"] = user.username
            return redirect("employees")
        return render(
            request,
            self.template_name,
            {"error": "Неверный логин или пароль"},
        )


class UserRegisterView(View):
    template_name = "core/register.html"
    success_url = reverse_lazy("login")

    def get(self, request):
        # Если пользователь уже авторизован — редирект
        if request.user.is_authenticated:
            return redirect("employees")
        return render(request, self.template_name)
        # return self.render_to_response()

    def post(self, request):
        user = User.objects.create_user(
            username=request.POST.get("username"),
            password=request.POST.get("password"),
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
        )

        Employee.objects.create(
            user=user,
            position=request.POST.get("position"),
            department=request.POST.get("department"),
        )

        return redirect(self.success_url)

    def render_to_response(self, **context):
        return TemplateView.as_view(
            template_name=self.template_name,
            extra_context=context,
        )(self.request)


class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = "core/employees.html"
    context_object_name = "employees"
    login_url = reverse_lazy("login")

    def get_queryset(self):
        return Employee.objects.select_related("user")
