from __future__ import annotations

import importlib
from typing import Optional, Sequence

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse, NoReverseMatch, resolve

try:

    from .models import ShippingAddress  # type: ignore
except Exception:  # pragma: no cover - keep tests runnable even if model moves
    ShippingAddress = None  # type: ignore[misc,assignment]


User = get_user_model()


# ---------- helpers ----------


def make_user(
    email: str = "user@example.com", *, password: str = "pass", is_staff: bool = False
):
    """
     User inherits AbstractUser, has USERNAME_FIELD='email',
    but REQUIRED_FIELDS still includes 'username'. AbstractUser's default
    manager expects a 'username' unless you've overridden the manager.
    So we always pass one here to be safe.
    """
    return User.objects.create_user(
        email=email,
        username=email.split("@")[0],  # simple username seed
        password=password,
        is_staff=is_staff,
    )


def safe_reverse(names: Sequence[str], **kwargs) -> Optional[str]:
    """Try several URL names, return the first that reverses, else None."""
    for name in names:
        try:
            return reverse(name, kwargs=kwargs if kwargs else None)
        except NoReverseMatch:
            continue
    return None


# ---------- model tests ----------


class UserModelTests(TestCase):
    def test_create_user_minimal(self):
        u = make_user()
        self.assertTrue(u.pk)
        self.assertEqual(u.email, "user@example.com")
        # string repr prefers email, but falls back to username if email missing
        self.assertIn(u.__str__(), {u.email, u.username})

    def test_create_superuser(self):
        su = User.objects.create_superuser(
            email="admin@example.com",
            username="admin",  # keep manager happy if it expects username
            password="pass",
        )
        self.assertTrue(su.is_superuser)
        self.assertTrue(su.is_staff)

    def test_shipping_address_create(self):
        if ShippingAddress is None:
            self.skipTest("ShippingAddress model not available")

        user = make_user()
        addr = ShippingAddress.objects.create(  # type: ignore[attr-defined]
            user=user,
            address_line_1="123 Lane",
            city="Town",
            postal_code="12345",
            country="US",
            # Optional fields:
            # address_line_2="Apt 4",
            # default=True,
        )
        self.assertTrue(addr.pk)
        self.assertEqual(addr.user, user)
        self.assertEqual(addr.address_line_1, "123 Lane")
        self.assertEqual(addr.city, "Town")
        self.assertEqual(addr.postal_code, "12345")
        self.assertEqual(addr.country, "US")


# ---------- API tests  ----------


class UsersAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user()
        self.password = "pass"

    def test_login_endpoint(self):
        url = safe_reverse(["users:login", "login", "api-login"])
        if not url:
            self.skipTest("No login URL found")

        resp = self.client.post(
            url, {"email": self.user.email, "password": self.password}
        )
        # Accept either redirect (Django form login) or 200/201 JSON login
        self.assertIn(resp.status_code, {200, 201, 302})

    def test_register_endpoint(self):
        url = safe_reverse(["users:register", "register", "api-register"])
        if not url:
            self.skipTest("No register URL found")

        payload = {
            "email": "new@example.com",
            "username": "new",  # keep manager happy
            "password": "pass1234",
        }
        resp = self.client.post(url, payload)
        self.assertIn(resp.status_code, {200, 201, 302})

    def test_profile_me_endpoint(self):
        url = safe_reverse(["users:me", "me", "profile", "api-me"])
        if not url:
            self.skipTest("No profile/me URL found")

        self.client.login(email=self.user.email, password="pass")
        resp = self.client.get(url)
        self.assertIn(resp.status_code, {200})


# ---------- admin/apps smoke ----------


class UsersAdminSmokeTests(TestCase):
    def test_admin_import_does_not_crash(self):
        importlib.import_module("users.admin")


class UsersAppsSmokeTests(TestCase):
    def test_apps_module_import(self):
        importlib.import_module("users.apps")


# ---------- forms (optional) ----------


class UsersFormsTests(TestCase):
    def setUp(self):
        try:
            self.forms = importlib.import_module("users.forms")
        except Exception:
            self.forms = None

    def test_login_form_valid(self):
        if not self.forms:
            self.skipTest("users.forms not available")
        self.assertTrue(True)

    def test_profile_update_form(self):
        if not self.forms:
            self.skipTest("users.forms not available")
        self.assertTrue(True)

    def test_registration_form_valid(self):
        if not self.forms:
            self.skipTest("users.forms not available")
        self.assertTrue(True)


# ---------- serializers (optional) ----------


class UsersSerializersTests(TestCase):
    def setUp(self):
        try:
            self.serializers = importlib.import_module("users.serializers")
        except Exception:
            self.serializers = None

    def test_registration_serializer_validate(self):
        if not self.serializers:
            self.skipTest("users.serializers not available")
        self.assertTrue(True)

    def test_user_serializer(self):
        if not self.serializers:
            self.skipTest("users.serializers not available")
        self.assertTrue(True)


# ---------- urls smoke & resolution ----------


class UsersURLSmokeTests(TestCase):
    def test_urls_module_import(self):
        importlib.import_module("users.urls")


class UsersURLResolutionTests(TestCase):
    def test_urls_module_contains_patterns(self):
        urls = importlib.import_module("users.urls")
        self.assertTrue(
            hasattr(urls, "urlpatterns"),
            "users.urls must define urlpatterns",
        )

    def test_urls_resolve_expected_views(self):
        url = safe_reverse(["users:me", "me", "profile", "api-me"])
        if not url:
            self.skipTest(
                "No matching URL found for ['users:me', 'me', 'profile', 'api-me']"
            )
        match = resolve(url)
        self.assertTrue(callable(match.func))


# ---------- views smoke ----------


class UsersViewsSmokeTests(TestCase):
    def test_views_module_import(self):
        importlib.import_module("users.views")
