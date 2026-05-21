from functools import wraps

from django.http import HttpResponseForbidden

from staff.models import Staff


def get_user_staff(user):
    if not getattr(user, "is_authenticated", False):
        return None

    try:
        return user.staff
    except (Staff.DoesNotExist, AttributeError):
        return None


def user_has_staff_role(user, role_name):
    staff = get_user_staff(user)
    normalized_role = (role_name or "").strip()

    if staff is None or not normalized_role:
        return False

    return staff.role.filter(name__iexact=normalized_role).exists()


def role_required(role_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not getattr(request.user, "is_authenticated", False):
                return HttpResponseForbidden(
                    "Vous devez vous connecter pour accéder à cette page."
                )

            if not user_has_staff_role(request.user, role_name):
                return HttpResponseForbidden(
                    "Accès interdit : votre compte doit avoir le rôle Caisse."
                )

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
