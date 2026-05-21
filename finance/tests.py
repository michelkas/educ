from decimal import Decimal

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from accounts.signals import create_user_profile, save_user_profile
from education.models import Classes, Section
from staff.models import Role, Staff
from students.models import Students

from .models import Box, Fees, MonthChoice
from .permissions import user_has_staff_role


class FinanceCashierAccessTestCase(TestCase):
    def setUp(self):
        post_save.disconnect(create_user_profile, sender=User)
        post_save.disconnect(save_user_profile, sender=User)
        self.section = Section.objects.create(name="Secondaire")
        self.classe = Classes.objects.create(name="1ere")
        self.student = Students.objects.create(
            name="Nsimba",
            surname="Kanku",
            first_name="Grace",
            classe=self.classe,
            section=self.section,
        )
        self.fees = Fees.objects.create(
            name="Minerval",
            amount=Decimal("100.00"),
            section=self.section,
        )
        self.fees.classe.add(self.classe)

    def tearDown(self):
        post_save.connect(create_user_profile, sender=User)
        post_save.connect(save_user_profile, sender=User)

    def create_staff_user(self, username, role_name):
        user = User.objects.create_user(username=username, password="pass")
        staff = Staff.objects.create(
            user=user,
            name="Mbuyi",
            surname="Kasongo",
            firstname="Alice",
        )
        role = Role.objects.create(name=role_name)
        staff.role.add(role)
        return user, staff

    def test_caisse_role_is_case_insensitive(self):
        user, _staff = self.create_staff_user("cashier", "Caisse")

        self.assertTrue(user_has_staff_role(user, "caisse"))
        self.assertTrue(user_has_staff_role(user, "Caisse"))

    def test_staff_with_caisse_role_can_create_payment(self):
        user, staff = self.create_staff_user("cashier", "Caisse")
        self.client.force_login(user)

        response = self.client.post(
            reverse("finance:add_payment"),
            {
                "student": self.student.id,
                "fees": self.fees.id,
                "month": MonthChoice.SEPTEMBRE,
                "amount_pay": "50.00",
                "type_paiement": "espece",
            },
        )

        payment = Box.objects.get()
        self.assertRedirects(
            response,
            reverse("finance:print_receipt", kwargs={"payment_id": payment.id}),
            fetch_redirect_response=False,
        )
        self.assertEqual(payment.collector, staff)

    def test_add_payment_page_uses_student_autocomplete(self):
        user, _staff = self.create_staff_user("cashier", "Caisse")
        self.client.force_login(user)

        response = self.client.get(reverse("finance:add_payment"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="student-search"')
        self.assertContains(response, reverse("finance:search_students"))

    def test_staff_without_caisse_role_cannot_create_payment(self):
        user, _staff = self.create_staff_user("teacher", "Professeur")
        self.client.force_login(user)

        response = self.client.post(
            reverse("finance:add_payment"),
            {
                "student": self.student.id,
                "fees": self.fees.id,
                "month": MonthChoice.SEPTEMBRE,
                "amount_pay": "50.00",
                "type_paiement": "espece",
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Box.objects.exists())

    def test_cashier_can_search_student_by_name_or_matricule(self):
        user, _staff = self.create_staff_user("cashier", "Caisse")
        self.client.force_login(user)

        response = self.client.get(
            reverse("finance:search_students"),
            {"q": f"{self.student.name} {self.student.first_name}"},
        )

        self.assertEqual(response.status_code, 200)
        students = response.json()["students"]
        self.assertEqual(len(students), 1)
        self.assertEqual(students[0]["id"], self.student.id)
        self.assertEqual(students[0]["classe"], self.classe.name)
        self.assertEqual(students[0]["matricule"], self.student.matricule)

        response = self.client.get(
            reverse("finance:search_students"),
            {"q": self.student.matricule[-3:]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["students"][0]["id"], self.student.id)

    def test_cashier_can_print_professional_receipt(self):
        user, staff = self.create_staff_user("cashier", "caisse")
        self.client.force_login(user)
        payment = Box.objects.create(
            student=self.student,
            fees=self.fees,
            month=MonthChoice.SEPTEMBRE,
            amount_pay=Decimal("100.00"),
            type_paiement="espece",
            collector=staff,
        )

        response = self.client.get(
            reverse("finance:print_receipt", kwargs={"payment_id": payment.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"REC-{payment.id:06d}")
        self.assertContains(response, "Total payé pour ce frais et ce mois")
        self.assertContains(response, "Signature et cachet")

    def test_payment_cannot_exceed_monthly_fee_with_installments(self):
        user, staff = self.create_staff_user("cashier", "Caisse")
        self.client.force_login(user)
        Box.objects.create(
            student=self.student,
            fees=self.fees,
            month=MonthChoice.SEPTEMBRE,
            amount_pay=Decimal("70.00"),
            type_paiement="espece",
            collector=staff,
        )

        response = self.client.post(
            reverse("finance:add_payment"),
            {
                "student": self.student.id,
                "fees": self.fees.id,
                "month": MonthChoice.SEPTEMBRE,
                "amount_pay": "40.00",
                "type_paiement": "espece",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Box.objects.count(), 1)
        self.assertContains(response, "Montant maximum autorisé")

    def test_direct_payment_creation_cannot_exceed_monthly_fee(self):
        user, staff = self.create_staff_user("cashier", "Caisse")
        self.client.force_login(user)

        with self.assertRaises(ValidationError):
            Box.objects.create(
                student=self.student,
                fees=self.fees,
                month=MonthChoice.SEPTEMBRE,
                amount_pay=Decimal("101.00"),
                type_paiement="espece",
                collector=staff,
            )

        self.assertFalse(Box.objects.exists())

    def test_future_month_payment_blocked_for_school_fee_with_previous_debt(self):
        user, staff = self.create_staff_user("cashier", "Caisse")
        self.client.force_login(user)
        Box.objects.create(
            student=self.student,
            fees=self.fees,
            month=MonthChoice.SEPTEMBRE,
            amount_pay=Decimal("50.00"),
            type_paiement="espece",
            collector=staff,
        )

        with self.assertRaises(ValidationError):
            Box.objects.create(
                student=self.student,
                fees=self.fees,
                month=MonthChoice.OCTOBRE,
                amount_pay=Decimal("100.00"),
                type_paiement="espece",
                collector=staff,
            )

    def test_future_month_payment_allowed_for_non_school_fee_with_previous_debt(self):
        user, staff = self.create_staff_user("cashier", "Caisse")
        self.client.force_login(user)
        non_school_fee = Fees.objects.create(
            name="Transport",
            amount=Decimal("30.00"),
            section=self.section,
        )
        non_school_fee.classe.add(self.classe)

        Box.objects.create(
            student=self.student,
            fees=non_school_fee,
            month=MonthChoice.SEPTEMBRE,
            amount_pay=Decimal("10.00"),
            type_paiement="espece",
            collector=staff,
        )

        payment = Box.objects.create(
            student=self.student,
            fees=non_school_fee,
            month=MonthChoice.OCTOBRE,
            amount_pay=Decimal("30.00"),
            type_paiement="espece",
            collector=staff,
        )

        self.assertEqual(payment.month, MonthChoice.OCTOBRE)

    def test_payment_edit_cannot_make_monthly_total_exceed_fee(self):
        user, staff = self.create_staff_user("cashier", "Caisse")
        self.client.force_login(user)
        first_payment = Box.objects.create(
            student=self.student,
            fees=self.fees,
            month=MonthChoice.SEPTEMBRE,
            amount_pay=Decimal("60.00"),
            type_paiement="espece",
            collector=staff,
        )
        Box.objects.create(
            student=self.student,
            fees=self.fees,
            month=MonthChoice.SEPTEMBRE,
            amount_pay=Decimal("40.00"),
            type_paiement="espece",
            collector=staff,
        )

        response = self.client.post(
            reverse("finance:edit_payment", kwargs={"payment_id": first_payment.id}),
            {
                "student": self.student.id,
                "fees": self.fees.id,
                "month": MonthChoice.SEPTEMBRE,
                "amount_pay": "70.00",
                "type_paiement": "espece",
            },
        )

        self.assertEqual(response.status_code, 200)
        first_payment.refresh_from_db()
        self.assertEqual(first_payment.amount_pay, Decimal("60.00"))
        self.assertContains(response, "Montant maximum autorisé")
