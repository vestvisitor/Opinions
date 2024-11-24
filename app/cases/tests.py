from lib2to3.fixes.fix_input import context

from django.contrib.auth import login
from django.db.transaction import commit
from django.test import TestCase
from django.contrib.auth.models import User
from django.shortcuts import reverse
from faker import Faker
from django.utils import timezone
import random
from django.db.models import Q
from .models import Opinion, Case, CaseTag, CaseOpinion
from .forms import CaseCreateForm, OpinionCreateForm, CaseEditForm
from .views import opinion

tests_settings = {
    "users_number": 5,
    "cases_number": 2,
    "opinions_number": 2,
    "tags": [
        "Education", "Friendship", "Hobbies",
        "Job\work", "Languages", "Medicine",
        "Relationships", "Sports"
    ]
}

fake = Faker()

def generate_user(username: str, email: str, password: str):
    return User.objects.create_user(
        username=username,
        email=email,
        password=password
    )


def generate_case(user: User, is_return: bool | None = False):
    form = CaseCreateForm(
        data={
            "case_title": fake.text(max_nb_chars=random.randint(15, 90)),
            "tags": CaseTag.objects.all()[(position := random.randint(1, 6)):position + 2],
            "case_text": fake.text(max_nb_chars=random.randint(200, 900)),
            "is_anonymous": True if random.randint(0, 1) == 1 else False,
        }
    )
    if form.is_valid():
        new = form.save(commit=False)
        new.pub_date = timezone.now()
        new.creator = user
        new.save()
        form.save_m2m()
        return new if is_return else None


def generate_opinion(case: Case, is_test_user: bool | None = False):

    if not is_test_user:
        while True:
            user = User.objects.exclude(pk=case.creator.pk)[random.randint(0,3)]
            try:
                condition1 = Q(case=case)
                condition2 = Q(opinion__creator__pk=user.pk)
                CaseOpinion.objects.get(condition1 & condition2)
            except CaseOpinion.DoesNotExist:
                break
            else:
                continue
    else:
        user = User.objects.get(pk=6)

    form = OpinionCreateForm(
        data = {
            "opinion_text": fake.text(max_nb_chars=random.randint(200, 900)),
            "is_anonymous": True if random.randint(0, 1) == 1 else False,
            "caseid": case.id
        },
        case_id = case.id
    )

    if form.is_valid():
        user_opinion = form.save(commit=False)

        user_opinion.creator = user
        user_opinion.case = case
        user_opinion.pub_date = timezone.now()

        user_opinion.save()
        form.save_m2m()

        data = CaseOpinion(
            case=case,
            opinion=user_opinion
        )
        data.save()


class CasesViewsTests(TestCase):

    @classmethod
    def setUpTestData(cls):

        for tag in tests_settings.get('tags'):
            CaseTag(tag_title=tag).save()

        for _ in range(tests_settings.get('users_number')):
            user = generate_user(
                username=fake.user_name(),
                email=fake.email(),
                password=fake.password(length=8)
            )
            for _ in range(tests_settings.get('cases_number')):
                generate_case(user)

        for case in Case.objects.all():
            for _ in range(tests_settings.get('opinions_number')):
                generate_opinion(case)

        cls.random_user = User.objects.get(pk=random.randint(1, tests_settings.get("users_number")))

        cls.username = "testuser"
        cls.email = "testuser@email.com"
        cls.password = "12345678"

        cls.test_user = generate_user(
            username=cls.username,
            email=cls.email,
            password=cls.password
        )

    def test_get_cases_page_unauthenticated(self):
        url = reverse("cases:index")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cases'], Case.objects.all().count())

    def test_get_my_cases_page_unauthenticated(self):
        url = reverse("cases:my_cases")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_get_existent_case_page_unauthenticated(self):
        case = Case.objects.get(pk=1)
        url = reverse("cases:case", kwargs={"case_id": case.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["case"].case_title, case.case_title)
        self.assertEqual(response.context["case"].case_text, case.case_text)
        self.assertEqual(response.context["case"].tags, case.tags)
        self.assertEqual(response.context["case"].is_anonymous, case.is_anonymous)
        self.assertEqual(response.context["case"].creator, case.creator)

    def test_get_nonexistent_case_page_unauthenticated(self):

        url = reverse("cases:case", kwargs={"case_id": "100"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_get_publish_case_page_unauthenticated(self):
        url = reverse("cases:publish")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_get_edit_case_page_unauthenticated(self):
        url = reverse("cases:edit", kwargs={"case_id": "1"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_get_my_opinions_page_unauthenticated(self):
        url = reverse("cases:opinions")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_post_delete_existent_case_unauthenticated(self):
        url = reverse("cases:delete", kwargs={"case_id": 1})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

    def test_post_delete_nonexistent_case_unauthenticated(self):
        url = reverse("cases:delete", kwargs={"case_id": 100})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

    def test_post_publish_case_unauthenticated(self):
        url = reverse("cases:publish")
        response = self.client.post(
            url,
            data={
                "case_title": fake.text(max_nb_chars=random.randint(15, 90)),
                "tags": CaseTag.objects.all()[1:3],
                "case_text": fake.text(max_nb_chars=random.randint(200, 900)),
                "is_anonymous": True if random.randint(0,1) == 1 else False
            }
        )

        self.assertEqual(response.status_code, 302)

    def test_post_edit_case_unauthenticated(self):
        url = reverse("cases:edit", kwargs={"case_id": 1})
        response = self.client.post(
            url,
            data={
                "case_title": fake.text(max_nb_chars=random.randint(15, 90)),
                "tags": CaseTag.objects.all()[1:3],
                "case_text": fake.text(max_nb_chars=random.randint(200, 900)),
                "is_anonymous": True if random.randint(0,1) == 1 else False
            }
        )

        self.assertEqual(response.status_code, 302)

    def test_post_opinion_unauthenticated(self):
        url = reverse("cases:opinion", kwargs={"case_id": 1})
        response = self.client.post(
            url,
            data={
                "opinion_text": fake.text(max_nb_chars=random.randint(200, 900)),
                "is_anonymous": True if random.randint(0,1) == 1 else False
            }
        )

        self.assertEqual(response.status_code, 302)

    def test_get_cases_page_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("cases:index")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cases'], Case.objects.exclude(creator=self.test_user.pk).count())

    def test_get_my_cases_empty_page_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("cases:my_cases")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cases'], Case.objects.filter(creator=self.test_user.pk).count())

    def test_get_my_cases_page_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        for _ in range(3):
            generate_case(self.test_user)
        url = reverse("cases:my_cases")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cases'], Case.objects.filter(creator=self.test_user.pk).count())

    def test_get_existent_my_case_page_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        case = generate_case(self.test_user, True)
        url = reverse("cases:case", kwargs={"case_id": case.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["case"].case_title, case.case_title)
        self.assertEqual(response.context["case"].case_text, case.case_text)
        self.assertEqual(response.context["case"].tags, case.tags)
        self.assertEqual(response.context["case"].is_anonymous, case.is_anonymous)
        self.assertEqual(response.context["case"].creator, case.creator)
        self.assertTrue(response.context["same"])

    def test_get_existent_other_not_commented_case_page_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        condition1 = ~Q(case__creator=self.test_user)
        condition2 = ~Q(opinion__creator=self.test_user)
        case_opinion = CaseOpinion.objects.filter(condition1 & condition2).first()
        url = reverse("cases:case", kwargs={"case_id": case_opinion.case.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["case"].case_title, case_opinion.case.case_title)
        self.assertEqual(response.context["case"].case_text, case_opinion.case.case_text)
        self.assertEqual(response.context["case"].tags, case_opinion.case.tags)
        self.assertEqual(response.context["case"].is_anonymous, case_opinion.case.is_anonymous)
        self.assertEqual(response.context["case"].creator, case_opinion.case.creator)
        self.assertIsInstance(response.context["form"], OpinionCreateForm)

    def test_get_existent_other_commented_case_page_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        case = Case.objects.get(pk=1)
        generate_opinion(case, True)
        url = reverse("cases:case", kwargs={"case_id": case.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["case"].case_title, case.case_title)
        self.assertEqual(response.context["case"].case_text, case.case_text)
        self.assertEqual(response.context["case"].tags, case.tags)
        self.assertEqual(response.context["case"].is_anonymous, case.is_anonymous)
        self.assertEqual(response.context["case"].creator, case.creator)
        self.assertNotContains(response, OpinionCreateForm)

    def test_get_nonexistent_case_page_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("cases:case", kwargs={"case_id": 100})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/cases/")

    def test_get_publish_case_page_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("cases:publish")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], CaseCreateForm)

    def test_get_edit_my_existent_case_page_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        case = generate_case(self.test_user, True)
        url = reverse("cases:edit", kwargs={"case_id": case.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], CaseEditForm)
        self.assertEqual(response.context['form']['case_title'].value(), case.case_title)
        self.assertEqual(response.context['form']["tags"].value(), [tag['id'] for tag in case.tags.values()])
        self.assertEqual(response.context['form']["case_text"].value(), case.case_text)
        self.assertEqual(response.context['form']["is_anonymous"].value(), case.is_anonymous)

    def test_get_edit_other_existent_case_page_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("cases:edit", kwargs={"case_id": 1})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_get_edit_nonexistent_case_page_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("cases:edit", kwargs={"case_id": 100})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_get_my_opinions_page_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("cases:opinions")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['opinions'], Opinion.objects.filter(creator=self.test_user).count())

    def test_post_delete_someones_case_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        case = Case.objects.get(pk=1)
        url = reverse("cases:delete", kwargs={"case_id": case.pk})
        response = self.client.post(url, follow=True)

        self.assertEqual(response.status_code, 403)

    def test_post_delete_nonexistent_case_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("cases:delete", kwargs={"case_id": 100})
        response = self.client.post(url, follow=True)

        self.assertEqual(response.status_code, 404)

    def test_post_delete_my_case_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        case = generate_case(self.test_user, True)
        url = reverse("cases:delete", kwargs={"case_id": case.pk})
        response = self.client.post(url, follow=True)

        self.assertEqual(response.status_code, 200)

    def test_post_publish_case_success_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("cases:publish")
        case_title = fake.text(max_nb_chars=random.randint(15, 90))
        tags = [tag[0] for tag in CaseTag.objects.values_list("id")][(position := random.randint(1, 6)):position + 2]
        case_text = fake.text(max_nb_chars=random.randint(200, 900))
        is_anonymous = True if random.randint(0, 1) == 1 else False
        response = self.client.post(
            url,
            follow=True,
            data={
                "case_title": case_title,
                "tags": tags,
                "case_text": case_text,
                "is_anonymous": is_anonymous
            }
        )
        case = Case.objects.get(creator=self.test_user)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(case.case_title, case_title)
        self.assertEqual([t.get('id') for t in case.tags.values()], tags)
        self.assertEqual(case.case_text, case_text)
        self.assertEqual(case.is_anonymous, is_anonymous)

    def test_post_publish_case_empty_is_anonymous_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("cases:publish")
        case_title = fake.text(max_nb_chars=random.randint(15, 90))
        tags = [tag[0] for tag in CaseTag.objects.values_list("id")][(position := random.randint(1, 6)):position + 2]
        case_text = fake.text(max_nb_chars=random.randint(200, 900))
        response = self.client.post(
            url,
            follow=True,
            data={
                "case_title": case_title,
                "tags": tags,
                "case_text": case_text
            }
        )
        case = Case.objects.get(creator=self.test_user)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(case.case_title, case_title)
        self.assertEqual([t.get('id') for t in case.tags.values()], tags)
        self.assertEqual(case.case_text, case_text)
        self.assertEqual(case.is_anonymous, False)

    def test_post_publish_case_empty_form_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("cases:publish")
        response = self.client.post(
            url,
            follow=True,
            data={
                "case_title": "",
                "tags": "",
                "case_text": "",
                "is_anonymous": ""
            }
        )

        self.assertEqual(response.status_code, 422)

    def test_post_publish_case_long_title_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("cases:publish")
        long_title = fake.text(max_nb_chars=300)
        response = self.client.post(
            url,
            follow=True,
            data={
                "case_title": long_title,
                "tags": [tag[0] for tag in CaseTag.objects.values_list("id")][(position := random.randint(1, 6)):position + 2],
                "case_text": fake.text(max_nb_chars=random.randint(200, 900)),
                "is_anonymous": True if random.randint(0, 1) == 1 else False
            }
        )

        self.assertLess(100, len(long_title))
        self.assertEqual(response.status_code, 422)

    def test_post_publish_case_long_text_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("cases:publish")
        long_text = fake.text(max_nb_chars=1300)
        response = self.client.post(
            url,
            follow=True,
            data={
                "case_title": fake.text(max_nb_chars=random.randint(15, 90)),
                "tags": [tag[0] for tag in CaseTag.objects.values_list("id")][(position := random.randint(1, 6)):position + 2],
                "case_text": long_text,
                "is_anonymous": True if random.randint(0, 1) == 1 else False
            }
        )

        self.assertLess(1000, len(long_text))
        self.assertEqual(response.status_code, 422)

    def test_post_publish_case_no_tags_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("cases:publish")
        response = self.client.post(
            url,
            follow=True,
            data={
                "case_title": fake.text(max_nb_chars=random.randint(15, 90)),
                "case_text": fake.text(max_nb_chars=random.randint(200, 900)),
                "is_anonymous": True if random.randint(0, 1) == 1 else False
            }
        )

        self.assertEqual(response.status_code, 422)

    def test_post_edit_case_success_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        case = generate_case(self.test_user, True)
        url = reverse("cases:edit", kwargs={"case_id": case.id})
        response = self.client.post(
            url,
            follow=True,
            data={
                "case_title": fake.text(max_nb_chars=random.randint(15, 90)),
                "tags": [tag[0] for tag in CaseTag.objects.values_list("id")][(position := random.randint(1, 6)):position + 2],
                "case_text": fake.text(max_nb_chars=900),
                "is_anonymous": False if case.is_anonymous else True
            }
        )
        edited_case = Case.objects.get(pk=case.pk)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(edited_case.case_title, case.case_title)
        self.assertNotEqual(edited_case.tags.values(), case.tags.values())
        self.assertNotEqual(edited_case.case_text, case.case_text)
        self.assertNotEqual(edited_case.is_anonymous, case.is_anonymous)

    def test_post_edit_long_title_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        case = generate_case(self.test_user, True)
        url = reverse("cases:edit", kwargs={"case_id": case.id})
        long_title = fake.text(max_nb_chars=300)
        response = self.client.post(
            url,
            follow=True,
            data={
                "case_title": long_title,
                "tags": [tag[0] for tag in CaseTag.objects.values_list("id")][(position := random.randint(1, 6)):position + 2],
                "case_text": fake.text(max_nb_chars=900),
                "is_anonymous": False if case.is_anonymous else True
            }
        )

        self.assertLess(100, len(long_title))
        self.assertEqual(response.status_code, 422)

    def test_post_edit_long_text_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        case = generate_case(self.test_user, True)
        url = reverse("cases:edit", kwargs={"case_id": case.id})
        long_text= fake.text(max_nb_chars=1300)
        response = self.client.post(
            url,
            follow=True,
            data={
                "case_title": fake.text(max_nb_chars=random.randint(15, 90)),
                "tags": [tag[0] for tag in CaseTag.objects.values_list("id")][(position := random.randint(1, 6)):position + 2],
                "case_text": long_text,
                "is_anonymous": False if case.is_anonymous else True
            }
        )

        self.assertLess(1000, len(long_text))
        self.assertEqual(response.status_code, 422)

    def test_post_edit_empty_tags_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        case = generate_case(self.test_user, True)
        url = reverse("cases:edit", kwargs={"case_id": case.id})
        response = self.client.post(
            url,
            follow=True,
            data={
                "case_title": fake.text(max_nb_chars=random.randint(15, 90)),
                "tags": [],
                "case_text": fake.text(max_nb_chars=900),
                "is_anonymous": False if case.is_anonymous else True
            }
        )

        self.assertEqual(response.status_code, 422)

    def test_post_edit_empty_form_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        case = generate_case(self.test_user, True)
        url = reverse("cases:edit", kwargs={"case_id": case.id})
        response = self.client.post(
            url,
            follow=True,
            data={
                "case_title": "",
                "tags": [],
                "case_text": "",
                "is_anonymous": ""
            }
        )

        self.assertEqual(response.status_code, 422)

    def test_post_opinion_success_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        case = Case.objects.get(pk=1)
        url = reverse("cases:opinion", kwargs={"case_id": case.id})
        response = self.client.post(
            url,
            follow=True,
            data={
                "opinion_text": (opinion_text := fake.text(max_nb_chars=random.randint(500, 900))),
                "is_anonymous": (is_anonymous := True if random.randint(0, 1) == 1 else False),
                "caseid": case.id,
            }
        )
        condition1 = Q(case=case)
        condition2 = Q(opinion__creator=self.test_user)
        caseopinion = CaseOpinion.objects.get(condition1 & condition2)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(caseopinion.case.case_title, case.case_title)
        self.assertEqual(caseopinion.case.tags, case.tags)
        self.assertEqual(caseopinion.case.case_text, case.case_text)
        self.assertEqual(caseopinion.case.is_anonymous, case.is_anonymous)
        self.assertEqual(caseopinion.opinion.opinion_text, opinion_text)
        self.assertEqual(caseopinion.opinion.is_anonymous, is_anonymous)
        self.assertEqual(caseopinion.opinion.creator, self.test_user)

    def test_post_opinion_twice_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        case = Case.objects.get(pk=1)
        url = reverse("cases:opinion", kwargs={"case_id": case.id})
        for _ in range(2):
            response = self.client.post(
                url,
                follow=True,
                data={
                    "opinion_text": fake.text(max_nb_chars=random.randint(500, 900)),
                    "is_anonymous": True if random.randint(0, 1) == 1 else False,
                    "caseid": case.id,
                }
            )

        self.assertEqual(response.status_code, 422)

    def test_post_opinion_nonexistent_case_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("cases:opinion", kwargs={"case_id": 100})
        response = self.client.post(
            url,
            follow=True,
            data={
                "opinion_text": fake.text(max_nb_chars=random.randint(500, 900)),
                "is_anonymous": True if random.randint(0, 1) == 1 else False,
                "caseid": 100,
            }
        )

        self.assertEqual(response.status_code, 404)

    def test_post_opinion_empty_text_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        case = Case.objects.get(pk=1)
        url = reverse("cases:opinion", kwargs={"case_id": case.id})
        response = self.client.post(
            url,
            follow=True,
            data={
                "opinion_text": "",
                "is_anonymous": True if random.randint(0, 1) == 1 else False,
                "caseid": case.id,
            }
        )

        self.assertEqual(response.status_code, 422)

    def test_post_opinion_empty_is_anonymous_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        case = Case.objects.get(pk=1)
        url = reverse("cases:opinion", kwargs={"case_id": case.id})
        response = self.client.post(
            url,
            follow=True,
            data={
                "opinion_text": fake.text(max_nb_chars=random.randint(500, 900)),
                "is_anonymous": "",
                "caseid": case.id,
            }
        )

        self.assertEqual(response.status_code, 200)

    def test_post_opinion_long_text_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        case = Case.objects.get(pk=1)
        url = reverse("cases:opinion", kwargs={"case_id": case.id})
        long_text = fake.text(max_nb_chars=1300)
        response = self.client.post(
            url,
            follow=True,
            data={
                "opinion_text": long_text,
                "is_anonymous": True if random.randint(0, 1) == 1 else False,
                "caseid": case.id,
            }
        )

        self.assertLess(1000, len(long_text))
        self.assertEqual(response.status_code, 422)
