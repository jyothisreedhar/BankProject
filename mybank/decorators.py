from .models import Account
from django.shortcuts import redirect
from django.contrib import messages
def account_validator(func):
    def wrapper(request, *args, **kwargs):
        try:
            account_details = Account.objects.get(user=request.user)
            status = account_details.active_status
            if status == "active":
                messages.error(request, "Account alredy created")
                return redirect("index")
            else:
                return func(request, *args, **kwargs)
        except:
            return func(request, *args, **kwargs)
    return wrapper
