
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import Students
from education.models import Section, Classes, Options

def students_list(request):
	"""
	Vue pour afficher la liste paginée des élèves, avec filtres par section, classe et option.

	Args:
		request (HttpRequest): La requête HTTP reçue.

	Returns:
		HttpResponse: La page HTML affichant la liste filtrée et paginée des élèves.
	"""
	# Récupération des paramètres de filtre depuis la requête GET
	section_id = request.GET.get('section')
	classe_id = request.GET.get('classe')
	option_id = request.GET.get('option')
	query = (request.GET.get('q') or '').strip()
	print_mode = request.GET.get('print') == '1'

	# Filtrage de la queryset des élèves selon les filtres sélectionnés
	students = Students.objects.select_related('user', 'classe', 'section', 'option').all()
	total_students = students.count()
	if section_id:
		students = students.filter(section_id=section_id)
	if classe_id:
		students = students.filter(classe_id=classe_id)
	if option_id:
		students = students.filter(option_id=option_id)
	if query:
		students = students.filter(
			Q(name__icontains=query) |
			Q(surname__icontains=query) |
			Q(first_name__icontains=query) |
			Q(matricule__icontains=query) |
			Q(user__username__icontains=query)
		)

	students = students.order_by('name', 'surname', 'first_name')
	filtered_count = students.count()

	# Récupération de toutes les sections, classes et options pour les filtres du template
	sections = Section.objects.all()
	classes = Classes.objects.all()
	options = Options.objects.all()

	# Pagination de la liste des élèves.
	per_page = filtered_count if print_mode and filtered_count else 10
	paginator = Paginator(students, per_page)
	page_number = 1 if print_mode else request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	today = timezone.localdate()
	for student in page_obj.object_list:
		if student.date_birthday:
			student.age = today.year - student.date_birthday.year - (
				(today.month, today.day) < (student.date_birthday.month, student.date_birthday.day)
			)
		else:
			student.age = None

	query_params = request.GET.copy()
	query_params.pop('page', None)
	query_params.pop('print', None)
	print_query_params = query_params.copy()
	print_query_params['print'] = '1'

	context = {
		'sections': sections,
		'classes': classes,
		'options': options,
		'page_obj': page_obj,
		'query': query,
		'query_string': query_params.urlencode(),
		'print_query_string': print_query_params.urlencode(),
		'print_mode': print_mode,
		'total_students': total_students,
		'filtered_count': filtered_count,
	}
	return render(request, 'students/students_list.html', context)

def register_student(request):
	pass
