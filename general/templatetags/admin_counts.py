from django import template
from django.db.models import Sum

register = template.Library()

@register.inclusion_tag('admin/admin_counts_panel.html', takes_context=True)
def admin_counts_panel(context):
    """Retourne les indicateurs principaux pour le tableau de bord admin."""
    def model_count(import_path, model_name):
        try:
            module = __import__(import_path, fromlist=[model_name])
            return getattr(module, model_name).objects.count()
        except Exception:
            return 0

    def aggregate_sum(import_path, model_name, field_name):
        try:
            module = __import__(import_path, fromlist=[model_name])
            value = getattr(module, model_name).objects.aggregate(total=Sum(field_name))["total"]
            return value or 0
        except Exception:
            return 0

    students_count = model_count("students.models", "Students")
    staff_count = model_count("staff.models", "Staff")
    classes_count = model_count("education.models", "Classes")
    courses_count = model_count("education.models", "Course")
    programs_count = model_count("general.models", "Program")
    events_count = model_count("general.models", "Actuality")
    contacts_count = model_count("general.models", "Contact")
    fees_count = model_count("finance.models", "Fees")
    payments_count = model_count("finance.models", "Box")
    total_paid = aggregate_sum("finance.models", "Box", "amount_pay")

    return {
        'students_count': students_count,
        'staff_count': staff_count,
        'classes_count': classes_count,
        'courses_count': courses_count,
        'programs_count': programs_count,
        'events_count': events_count,
        'contacts_count': contacts_count,
        'fees_count': fees_count,
        'payments_count': payments_count,
        'total_paid': total_paid,
    }
