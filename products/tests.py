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
            email="admin@example.com", password="pass"
        )
        self.client = Client()
        self.client.login(email="admin@example.com", password="pass")

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

    def test_add_inline_tech_spec_via_admin_change(self):
        change_url = reverse("admin:products_product_change", args=[self.product.id])

        # Load change form to get CSRF etc.
        resp = self.client.get(change_url)
        self.assertEqual(resp.status_code, 200)

        # Post minimal product fields + inline formset
        # Prefix Django uses for default TabularInline: "<modelname>_set"
        prefix = "producttechspec_set"

        post_data = {
            "name": self.product.name,
            "slug": self.product.slug,
            "category": str(self.category.id),
            "description": self.product.description,
            "price": str(self.product.price),
            "currency": self.product.currency,
            "stock": str(self.product.stock),
            "unit_measure": self.product.unit_measure,
            "available": "on",  # checkbox
            # inline management form
            f"{prefix}-TOTAL_FORMS": "1",
            f"{prefix}-INITIAL_FORMS": "0",
            f"{prefix}-MIN_NUM_FORMS": "0",
            f"{prefix}-MAX_NUM_FORMS": "1000",
            # inline row 0 (our friendly fields)
            f"{prefix}-0-id": "",
            f"{prefix}-0-spec_name": "Alpha Acids",
            f"{prefix}-0-spec_value": "12%, 13%, 14%",
        }

        resp = self.client.post(change_url, post_data, follow=True)
        self.assertEqual(resp.status_code, 200)

        # One tech spec should be created and normalized by the form
        self.assertEqual(self.product.tech_specs.count(), 1)
        ts = self.product.tech_specs.first()
        self.assertEqual(
            ts.tech_spec,
            {"name": "Alpha Acids", "value": ["12%", "13%", "14%"]},
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
