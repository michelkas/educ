from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Fees
from .permissions import role_required
from students.models import Students


@login_required
@role_required('caisse')
def get_fees_for_student(request):
    student_id = request.GET.get('student_id')
    try:
        student = Students.objects.get(pk=student_id)
        fees = Fees.objects.filter(section=student.section, classe=student.classe)
        data = [
            {'id': fee.id, 'name': fee.name, 'amount': float(fee.amount)}
            for fee in fees
        ]
        return JsonResponse({'fees': data})
    except Students.DoesNotExist:
        return JsonResponse({'fees': []})


@login_required
@role_required('caisse')
def search_students(request):
    query = (request.GET.get('q') or '').strip()

    if len(query) < 2:
        return JsonResponse({'students': []})

    students = (
        Students.get_students_for_payment()
        .select_related('classe', 'section', 'option')
        .order_by('name', 'surname', 'first_name')
    )
    for term in query.split():
        students = students.filter(
            Q(matricule__icontains=term)
            | Q(name__icontains=term)
            | Q(surname__icontains=term)
            | Q(first_name__icontains=term)
        )
    students = students[:10]

    data = []
    for student in students:
        full_name = f"{student.name} {student.surname} {student.first_name}".strip()
        classe = student.classe.name if student.classe else "-"
        section = student.section.name if student.section else "-"
        option = student.option.name if student.option else "-"
        data.append({
            'id': student.id,
            'full_name': full_name,
            'matricule': student.matricule,
            'classe': classe,
            'section': section,
            'option': option,
            'label': f"{full_name} - {student.matricule}",
        })

    return JsonResponse({'students': data})
