from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.text import slugify
from django.urls import reverse


class JournalizedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class Category(JournalizedModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/products/category/{self.slug}/"


class Product(JournalizedModel):
    """
    Represents a product available in the inventory system.

    This class is used to define and manage the details of a product in the system.
     It inherits from the `JournalizedModel` to track changes
     and support auditing of the product details.

    :ivar name: The name of the product.
    :ivar slug: A unique slug generated for the product, used for URLs.
    :ivar category: The category to which the product belongs.
    :ivar description: Detailed description of the product.
    :ivar price: The price of the product.
    :ivar currency: The currency in which the product price is denoted.
    :ivar stock: The total available stock for the product.
    :ivar unit_measure: The unit in which the product is measured (e.g., kg, lb).
    :ivar image: An optional image of the product.
    :ivar available: A boolean indicating whether the product is available for sale.
    """

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(max_length=1000)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    stock = models.PositiveIntegerField()
    unit_measure = models.TextField(max_length=5, default="kg")
    image = models.ImageField(upload_to="product_images/", null=True, blank=True)
    available = models.BooleanField(default=True)

    class Meta:
        verbose_name = "product"
        verbose_name_plural = "products"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("products:product-detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductReview(JournalizedModel):
    """
    Represents a product review within the system.

    This class is used to define, manage, and interact with reviews provided
    by users for specific products. Reviews include information such as
    the user who provided the review, the product being reviewed, the rating
    assigned, an optional title, and a detailed comment. This can help in
    analyzing user feedback and improving products based on customer insights.

    :ivar product: The product to which this review belongs.
    :ivar user: The user who provided this review.
    :ivar rating: The numerical rating provided for the product, within a
        valid range of 1 to 5.
    :ivar title: An optional short title for the review, defined by the user.
    :ivar comment: A detailed comment providing further information or feedback
        about the product.
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.TextField(max_length=50, blank=True, null=True)
    comment = models.TextField(max_length=1000)

    class Meta:
        verbose_name = "Product Review"
        verbose_name_plural = "Product Reviews"

    def __str__(self):
        return (
            f"{self.user.email} - {self.product.name} - {self.rating} - "
            f"{self.title}"
        )


class ProductTechSpec(models.Model):
    """
    Represents the technical specifications of a product.

    This Django model stores technical specifications of a product in
    JSON format.
    Each instance of the model is associated with a specific product.

    :ivar product: The product foreign key associated with the technical
                    specifications.
    :ivar tech_spec: JSON storing the technical specifications of the product
                    May be none or empty. Shall include two key:value pairs:
        key "name" suits for Specification Name, String value
        key "value" suits for Specification Value. May be String or
            List of objects.
        - **String values** like `"USA"` are displayed as `"USA"`
        - **List values** like `["Red", "Blue"]` are displayed as `"Red, Blue"`
        - **Complex lists** like `[{"name": "Size", "value": "Large"}]`
                            are displayed  as `"Size: Large"`
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="tech_specs"
    )
    tech_spec = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} Tech Specs"

    class Meta:
        verbose_name = "Product Tech Spec"
        verbose_name_plural = "Product Tech Specs"
