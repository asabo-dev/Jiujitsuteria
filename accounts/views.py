from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm


# -------------------------
# Custom Login View
# -------------------------
class CustomLoginView(LoginView):
    template_name = "registration/login.html"  # your login.html
    authentication_form = CustomLoginForm


# -------------------------
# Staff-only check
# -------------------------
def staff_check(user):
    return user.is_staff


# -------------------------
# Staff-only upload view
# -------------------------
@user_passes_test(staff_check)
@login_required
def upload_video(request):
    if request.method == "POST":
        # TODO: handle file upload + save to DB
        pass
    return render(request, "bjj/upload_video.html")
