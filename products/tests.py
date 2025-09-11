from __future__ import annotations


from django.contrib import admin
from django.contrib.auth import get_user_model

from django.test import Client, TestCase
from django.urls import reverse

from products.admin import ProductAdmin, ProductTechSpecInline
from products.admin_forms import ProductTechSpecJSONForm
from products.models import Category, Product, ProductTechSpec


class ProductTechSpecJSONFormTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Hops", slug="hops")
        self.product = Product.objects.create(
            name="Mosaic Hops",
            slug="mosaic-hops",
            category=self.category,
            description="Aromatic hops",
            price="10.00",
            currency="USD",
            stock=25,
            unit_measure="kg",
            available=True,
        )

    def test_form_string_value(self):
        form = ProductTechSpecJSONForm(
            data={"spec_name": "Country", "spec_value": "USA"},
            instance=ProductTechSpec(product=self.product),
        )
        self.assertTrue(form.is_valid(), form.errors)
        inst = form.save()
        self.assertEqual(inst.product, self.product)
        self.assertEqual(inst.tech_spec, {"name": "Country", "value": "USA"})

    def test_form_list_value_comma_separated(self):
        form = ProductTechSpecJSONForm(
            data={"spec_name": "Colors", "spec_value": "Red, Blue ,  Green"},
            instance=ProductTechSpec(product=self.product),
        )
        self.assertTrue(form.is_valid(), form.errors)
        inst = form.save()
        self.assertEqual(
            inst.tech_spec,
            {"name": "Colors", "value": ["Red", "Blue", "Green"]},
        )

    def test_form_name_value_pairs(self):
        # supports "key: value" pairs, comma-separated
        form = ProductTechSpecJSONForm(
            data={
                "spec_name": "Attributes",
                "spec_value": "Alpha: 12%, Beta: 4.5%, Cohumulone: 25",
            },
            instance=ProductTechSpec(product=self.product),
        )
        self.assertTrue(form.is_valid(), form.errors)
        inst = form.save()
        self.assertEqual(
            inst.tech_spec,
            {
                "name": "Attributes",
                "value": [
                    {"name": "Alpha", "value": "12%"},
                    {"name": "Beta", "value": "4.5%"},
                    {"name": "Cohumulone", "value": "25"},
                ],
            },
        )

    def test_missing_name_is_invalid(self):
        form = ProductTechSpecJSONForm(
            data={"spec_name": "", "spec_value": "Something"},
            instance=ProductTechSpec(product=self.product),
        )
        self.assertFalse(form.is_valid())
        self.assertIn("spec_name", form.errors)

    def test_blank_value_allowed(self):
        form = ProductTechSpecJSONForm(
            data={"spec_name": "EmptyAllowed", "spec_value": ""},
            instance=ProductTechSpec(product=self.product),
        )
        self.assertTrue(form.is_valid(), form.errors)
        inst = form.save()
        self.assertEqual(inst.tech_spec, {"name": "EmptyAllowed", "value": ""})


class ProductAdminInlineWiringTests(TestCase):
    def test_inline_registered_and_fields(self):
        ma = admin.site._registry[Product]
        # the actual ProductAdmin instance

        # Assert the inline class is registered (Django stores classes here)
        self.assertIn(ProductTechSpecInline, getattr(ma, "inlines", []))

        # Optionally verify the inline exposes the friendly fields
        inline_instance = ProductTechSpecInline(Product, admin.site)
        self.assertEqual(tuple(inline_instance.fields), ("spec_name", "spec_value"))


class ProductAdminInlinePostTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.superuser = User.objects.create_superuser(
            username="admin",  # shim just for the manager
            email="admin@example.com",
            password="pass",
        )
        self.client = Client()
        self.client.force_login(self.superuser)  # avoid credential-based login

        self.category = Category.objects.create(name="Hops", slug="hops")
        self.product = Product.objects.create(
            name="Mosaic Hops",
            slug="mosaic-hops",
            category=self.category,
            description="Aromatic hops",
            price="10.00",
            currency="USD",
            stock=25,
            unit_measure="kg",
            available=True,
        )


class ProductDetailViewTechSpecsRenderTests(TestCase):
    """
    Verifies the view's context processing that converts the stored JSON
    into human-friendly strings (the same logic your template consumes).
    """

    def setUp(self):
        User = get_user_model()
        self.superuser = User.objects.create_superuser(
            username="admin",  # <-- shim to satisfy manager
            email="admin@example.com",
            password="pass",
        )
        self.client = Client()
        self.client.force_login(self.superuser)
        self.category = Category.objects.create(name="Hops", slug="hops")
        self.product = Product.objects.create(
            name="Mosaic Hops",
            slug="mosaic-hops",
            category=self.category,
            description="Aromatic hops",
            price="10.00",
            currency="USD",
            stock=25,
            unit_measure="kg",
            available=True,
        )

        # (1) simple string
        ProductTechSpec.objects.create(
            product=self.product,
            tech_spec={"name": "Country", "value": "USA"},
        )
        # (2) simple list
        ProductTechSpec.objects.create(
            product=self.product,
            tech_spec={"name": "Colors", "value": ["Red", "Blue"]},
        )
        # (3) list of {"name","value"} objects
        ProductTechSpec.objects.create(
            product=self.product,
            tech_spec={
                "name": "Attributes",
                "value": [
                    {"name": "Alpha", "value": "12%"},
                    {"name": "Beta", "value": "4.5%"},
                ],
            },
        )

    def test_view_context_formats_values(self):
        url = reverse("products:product-detail", kwargs={"slug": self.product.slug})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        tech_specs = resp.context["tech_specs"]

        # turn list of dicts into an indexable map for easy asserts
        by_name = {row["name"]: row["value"] for row in tech_specs}

        self.assertIn("Country", by_name)
        self.assertEqual(by_name["Country"], "USA")

        self.assertIn("Colors", by_name)
        self.assertEqual(by_name["Colors"], "Red, Blue")

        self.assertIn("Attributes", by_name)
        self.assertEqual(by_name["Attributes"], "Alpha: 12%, Beta: 4.5%")


# Create your tests here.
