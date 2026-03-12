from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView

from .models import Employee
from .forms import UserRegistrationForm


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


class UserLogoutView(View):
    template_name = "core/login.html"

    def get(self, request):
        logout(request)
        return render(request, self.template_name)


class UserRegisterView(View):
    template_name = "core/register.html"
    success_url = reverse_lazy("login")

    def get(self, request):
        # Если пользователь уже авторизован — редирект
        if request.user.is_authenticated:
            return redirect("employees")
        form = UserRegistrationForm()
        return render(request, self.template_name, {'form': form})
        # return self.render_to_response()

    def post(self, request):
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            try:
                # Создаем пользователя
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                )

                # Создаем сотрудника
                Employee.objects.create(
                    user=user,
                    position=form.cleaned_data['position'],
                    department=form.cleaned_data['department'],
                    sector=form.cleaned_data.get('sector', ''),
                )

                return redirect(self.success_url)
            except Exception as e:
                # В случае ошибки при создании, добавляем сообщение в форму
                form.add_error(None, f'Ошибка при регистрации: {str(e)}')

        # Если форма не валидна, возвращаем страницу с ошибками
        return render(request, self.template_name, {'form': form})


class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = "core/employees.html"
    context_object_name = "employees"
    login_url = reverse_lazy("login")

    def get_queryset(self):
        return Employee.objects.select_related("user")
