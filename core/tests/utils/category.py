import random
from authentication.models import User
from core.models import Category
def create_random_category(user: User) -> Category:
    """
    Utility function to create and save a random Category for the given user.
    """
    category_names = ["Groceries", "Electronics", "Clothing", "Books", "Health & Beauty"]
    name = random.choice(category_names)
    
    category = Category.objects.create(
        user=user,
        name=name
    )
    return category   

def create_random_categories(user: User, count: int) -> list[Category]:
    """
    Utility function to create and save multiple random Categories for the given user.
    """
    categories = []
    for _ in range(count):
        category = create_random_category(user)
        categories.append(category)
    return categories