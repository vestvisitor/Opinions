from django.contrib.auth import login
from django.test import TestCase
from django.contrib.auth.models import User
from django.shortcuts import reverse
from faker import Faker
import random

tests_settings = {
    "users_number": 5,
}


class UsersViewsTests(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.username = "testuser"
        cls.email = "testuser@email.com"
        cls.password = "12345678"

        cls.test_user = User.objects.create_user(
            username=cls.username,
            email=cls.email,
            password=cls.password
        )

        cls.username_signup = "NewUserUsername"
        cls.email_signup = "NewUserEmail@email.com"
        cls.password_signup = "NeW0z3r7as5w0Rd"

        cls.fake = Faker()

        for _ in range(tests_settings.get('users_number')):
            User.objects.create_user(
                username=cls.fake.user_name(),
                email=cls.fake.email(),
                password=cls.fake.password(length=8)
            )

        cls.random_user = User.objects.get(pk=random.randint(2, tests_settings.get("users_number")+1))

    def test_get_users_page_unauthenticated(self):
        url = reverse("users:index")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_get_signin_page_unauthenticated(self):
        url = reverse("users:signin")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_get_signup_page_unauthenticated(self):
        url = reverse("users:signup")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_get_profile_page_unauthenticated(self):
        user = User.objects.get(pk=random.randint(1,tests_settings.get('users_number')+1))
        url = reverse("users:profile", kwargs={"username": user.username})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_get_nonexistent_profile_page_unauthenticated(self):
        url = reverse("users:profile", kwargs={"username": "UserDoesntExist"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_get_me_page_unauthenticated(self):
        url = reverse("users:me")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_get_edit_profile_page_unauthenticated(self):
        url = reverse("users:edit")
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

    def test_get_edit_password_page_unauthenticated(self):
        url = reverse("users:edit_password")
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

    def test_post_signin_success_unauthenticated(self):
        url = reverse("users:signin")
        response = self.client.post(
            url,
            data={
                "username": self.test_user.username,
                "password": self.password
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

    def test_post_signin_wrong_username_unauthenticated(self):
        url = reverse("users:signin")
        response = self.client.post(
            url,
            data={
                "username": f"{self.test_user.username}f",
                "password": self.password
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/signin/")

    def test_post_signin_wrong_password_unauthenticated(self):
        url = reverse("users:signin")
        response = self.client.post(
            url,
            data={
                "username": self.test_user.username,
                "password": f"{self.password}1"
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/signin/")

    def test_post_signup_success_unauthenticated(self):
        url = reverse("users:signup")
        response = self.client.post(
            url,
            data={
                "username": self.username_signup,
                "email": self.email_signup,
                "password1": self.password_signup,
                "password2": self.password_signup
            }
        )
        created_user = User.objects.get(username=self.username_signup)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        self.assertEqual(created_user.username, self.username_signup)
        self.assertEqual(created_user.email, self.email_signup)

    def test_post_signup_different_passwords_unauthenticated(self):
        url = reverse("users:signup")
        response = self.client.post(
            url,
            data={
                "username": self.username_signup,
                "email": self.email_signup,
                "password1": self.password_signup,
                "password2": f"{self.password_signup}2"
            }
        )

        self.assertEqual(response.status_code, 409)

    def test_post_signup_short_passwords_unauthenticated(self):
        url = reverse("users:signup")
        response = self.client.post(
            url,
            data={
                "username": self.username_signup,
                "email": self.email_signup,
                "password1": self.password_signup[:-8],
                "password2": self.password_signup[:-8]
            }
        )

        self.assertEqual(response.status_code, 409)

    def test_post_signup_numberic_passwords_unauthenticated(self):
        url = reverse("users:signup")
        response = self.client.post(
            url,
            data={
                "username": self.username_signup,
                "email": self.email_signup,
                "password1": "12345678",
                "password2": "12345678"
            }
        )

        self.assertEqual(response.status_code, 409)

    def test_post_signup_too_common_passwords_unauthenticated(self):
        url = reverse("users:signup")
        response = self.client.post(
            url,
            data={
                "username": self.username_signup,
                "email": self.email_signup,
                "password1": "qweasd123",
                "password2": "qweasd123"
            }
        )

        self.assertEqual(response.status_code, 409)

    def test_post_signup_existent_username_unauthenticated(self):
        url = reverse("users:signup")
        response = self.client.post(
            url,
            data={
                "username": self.test_user.username,
                "email": self.email_signup,
                "password1": self.password_signup,
                "password2": self.password_signup
            }
        )

        self.assertEqual(response.status_code, 409)

    def test_post_signup_existent_email_unauthenticated(self):
        url = reverse("users:signup")
        response = self.client.post(
            url,
            data={
                "username": self.username_signup,
                "email": self.test_user.email,
                "password1": self.password_signup,
                "password2": self.password_signup
            }
        )

        self.assertEqual(response.status_code, 409)

    def test_post_signup_invalid_email_unauthenticated(self):
        url = reverse("users:signup")
        response = self.client.post(
            url,
            data={
                "username": self.username_signup,
                "email": "notemailatall",
                "password1": self.password_signup,
                "password2": self.password_signup
            }
        )

        self.assertEqual(response.status_code, 409)

    def test_post_signup_long_username_unauthenticated(self):
        url = reverse("users:signup")
        long_username = "".join(self.fake.random_elements(("a", "b"), 151))
        response = self.client.post(
            url,
            data={
                "username": long_username,
                "email": self.email_signup,
                "password1": self.password_signup,
                "password2": self.password_signup
            }
        )

        self.assertEqual(response.status_code, 409)

    def test_post_signup_empty_form_unauthenticated(self):
        url = reverse("users:signup")
        response = self.client.post(
            url,
            data={
                "username": "",
                "email": "",
                "password1": "",
                "password2": ""
            }
        )

        self.assertEqual(response.status_code, 409)

    def test_post_edit_profile_page_unauthenticated(self):
        url = reverse("users:edit")
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

    def test_post_logout_unauthenticated(self):
        url = reverse("users:signout")
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

    def test_post_edit_password_page_unauthenticated(self):
        url = reverse("users:edit_password")
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

    def test_get_users_page_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:index")
        response = self.client.get(url, follow=True)

        self.assertNotIn(self.test_user, response.context['page_obj'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['authenticated'], True)

    def test_get_signin_page_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:signin")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_get_signup_page_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:signup")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_get_testuser_profile_page_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:profile", kwargs={"username": f"{self.test_user.username}"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_get_profile_page_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:profile", kwargs={"username": self.random_user.username})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_get_nonexistent_profile_page_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:profile", kwargs={"username": "UserDoesntExist"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_get_me_page_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:me")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_get_edit_profile_page_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:edit")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form']['username'].value(), self.test_user.username)
        self.assertEqual(response.context['form']['email'].value(), self.test_user.email)

    def test_get_edit_password_page_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:edit")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_post_edit_profile_without_change_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:edit")
        self.client.post(
            url,
            follow=True,
            data={"username": self.test_user.username, "email": self.test_user.email}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form']['username'].value(), self.test_user.username)
        self.assertEqual(response.context['form']['email'].value(), self.test_user.email)

    def test_post_edit_profile_change_username_to_nonexistent_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:edit")
        self.client.post(
            url,
            follow=True,
            data={"username": (unique_username := "UsernameDoesNotExist"), "email": self.test_user.email}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form']['username'].value(), unique_username)
        self.assertEqual(response.context['form']['email'].value(), self.test_user.email)

    def test_post_edit_profile_change_username_to_existent_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:edit")
        self.client.post(
            url,
            follow=True,
            data={"username": self.random_user.username}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.context['form']['username'].value(), self.random_user.username)
        self.assertEqual(response.context['form']['email'].value(), self.test_user.email)

    def test_post_edit_profile_change_email_to_nonexistent_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:edit")
        self.client.post(
            url,
            follow=True,
            data={"username": self.test_user.username, "email": (unique_email := "EmailDoesNotExist@email.com")}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form']['username'].value(), self.test_user.username)
        self.assertEqual(response.context['form']['email'].value(), unique_email)

    def test_post_edit_profile_change_email_to_existent_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:edit")
        self.client.post(
            url,
            follow=True,
            data={"email": self.random_user.email}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form']['username'].value(), self.test_user.username)
        self.assertNotEqual(response.context['form']['email'].value(), self.random_user.email)

    def test_post_edit_profile_change_username_email_to_nonexistent_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:edit")
        self.client.post(
            url,
            follow=True,
            data={
                "username": (unique_username := "UsernameDoesNotExist"),
                "email": (unique_email := "EmailDoesNotExist@email.com")
            }
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form']['username'].value(), unique_username)
        self.assertEqual(response.context['form']['email'].value(), unique_email)

    def test_post_edit_profile_change_username_email_to_existent_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:edit")
        self.client.post(
            url,
            follow=True,
            data={
                "username": self.random_user.username,
                "email": self.random_user.email
            }
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.context['form']['username'].value(), self.random_user.username)
        self.assertNotEqual(response.context['form']['email'].value(), self.random_user.email)

    def test_post_edit_profile_change_username_to_empty_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:edit")
        self.client.post(
            url,
            follow=True,
            data={
                "username": ""
            }
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.context['form']['username'].value(), "")
        self.assertEqual(response.context['form']['email'].value(), self.test_user.email)

    def test_post_edit_profile_change_email_to_empty_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:edit")
        self.client.post(
            url,
            follow=True,
            data={
                "email": ""
            }
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form']['username'].value(), self.test_user.username)
        self.assertNotEqual(response.context['form']['email'].value(), "")

    def test_post_edit_profile_change_username_to_invalid_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:edit")
        long_username = "".join(self.fake.random_elements(("a", "b"), 151))
        self.client.post(
            url,
            follow=True,
            data={
                "username": long_username,
            }
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.context['form']['username'].value(), long_username)
        self.assertEqual(response.context['form']['email'].value(), self.test_user.email)

    def test_post_edit_profile_change_email_to_invalid_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:edit")
        self.client.post(
            url,
            follow=True,
            data={
                "email": "somerandomemail.com"
            }
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form']['username'].value(), self.test_user.username)
        self.assertNotEqual(response.context['form']['email'].value(), "somerandomemail.com")

    def test_post_edit_password_empty_form_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:edit_password")
        self.client.post(
            url,
            follow=True,
            data={
                "old_password": "",
                "new_password1": "",
                "new_password2": ""
            }
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_post_edit_password_wrong_old_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:edit_password")
        self.client.post(
            url,
            follow=True,
            data={
                "old_password": self.password[:-1],
                "new_password1": (new_password := self.fake.password(length=8)),
                "new_password2": new_password
            }
        )
        response = self.client.get(url)
        user = User.objects.get(pk=self.test_user.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.password, self.test_user.password)

    def test_post_edit_password_new_short_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:edit_password")
        self.client.post(
            url,
            follow=True,
            data={
                "old_password": self.password,
                "new_password1": (new_password := self.fake.password(length=7)),
                "new_password2": new_password
            }
        )
        response = self.client.get(url)
        user = User.objects.get(pk=self.test_user.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.password, self.test_user.password)

    def test_post_edit_password_new_different_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:edit_password")
        self.client.post(
            url,
            follow=True,
            data={
                "old_password": self.password,
                "new_password1": (new_password := self.fake.password(length=8)),
                "new_password2": f"{new_password}2"
            }
        )
        response = self.client.get(url)
        user = User.objects.get(pk=self.test_user.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.password, self.test_user.password)

    def test_post_edit_password_success_authenticated(self):
        self.client.login(username=self.test_user.username, password=self.password)
        url = reverse("users:edit_password")
        self.client.post(
            url,
            follow=True,
            data={
                "old_password": self.password,
                "new_password1": (new_password := self.fake.password(length=8)),
                "new_password2": new_password
            }
        )
        response = self.client.get(url)
        user = User.objects.get(pk=self.test_user.pk)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(user.password, self.test_user.password)

    def test_post_logout_authenticated(self):
            self.client.login(username=self.test_user.username, password=self.password)
            url = reverse("users:signout")
            response = self.client.post(url, follow=True)

            self.assertEqual(response.status_code, 200)
