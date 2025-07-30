import random
from django.utils import timezone
from core.models import Product, Category, User

def create_random_product(user: User, category: None | Category = None, set_random_category=False) -> Product:
    """
    Utility function to create and save a random Product for the given user.
    """
    # Example random data
    product_names = ["Bread", "Milk", "Eggs", "Butter", "Juice", "Cheese", "Apple", "Banana", "Chicken", "Rice"]
    descriptions = [
        "Fresh and tasty.",
        "Best quality.",
        "Limited edition.",
        "Organic product.",
        "Imported goods.",
        "Locally sourced.",
        "On sale.",
        "Family pack.",
        "Gluten free.",
        "Sugar free."
    ]
    categories = Category.objects.filter(user=user)
    if set_random_category:
        category = random.choice(categories) if categories.exists() else None
    else:
        category = category

    name = random.choice(product_names)
    price = round(random.uniform(1.0, 100.0), 2)
    description = random.choice(descriptions)
    date = timezone.now() - timezone.timedelta(days=random.randint(0, 30))

    product = Product.objects.create(
        user=user,
        name=name,
        category=category,
        price=price,
        date=date,
        description=description
    )
    return product

def create_random_products(user: User, count: int, category: None | Category = None, set_random_category=False) -> list[Product]:
    """
    Utility function to create and save multiple random Products for the given user.
    """
    products = []
    for _ in range(count):
        product = create_random_product(user, category, set_random_category)
        products.append(product)
    return products