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
    Represents a product in the inventory system.

    This class is used to define the structure and behavior of a product entity
    in the inventory management context. It includes fields such as name, price,
    category, and stock, among others, and provides essential methods like string
    representation, URL generation, and slug generation upon saving.

    :ivar name: The name of the product.
    :type name: str
    :ivar slug: A unique slug identifier for the product.
    :type slug: str
    :ivar category: The category associated with the product.
    :type category: Category
    :ivar description: A detailed description of the product with a maximum of
        1000 characters.
        >>The first sentence of the description to be less than 30 chars and
        would be used as a short description for product card in the List
        View being truncated by final comma.
        >>Otherwise first 30 chars would be used with no regards to comma split.
    :type description: str
    :ivar price: The price of the product, encompassing up to 10 digits with
        2 decimal places.
    :type price: decimal.Decimal
    :ivar currency: The currency code for the product price (ISO 4217 format).
    :type currency: str
    :ivar stock: The quantity of the product currently available in stock.
    :type stock: int
    :ivar unit_measure: The unit of measure for the product, defaulting to "kg".
    :type unit_measure: str
    :ivar image: An optional image associated with the product.
    :type image: models.ImageField
    :ivar available: Indicates whether the product is available (defaults to True).
    :type available: bool
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
