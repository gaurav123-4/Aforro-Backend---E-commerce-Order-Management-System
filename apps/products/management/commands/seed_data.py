from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from apps.products.models import Category, Product, Store, Inventory
from apps.orders.models import Order, OrderItem
import random

fake = Faker()


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data before seeding')

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Category.objects.all().delete()
            Product.objects.all().delete()
            Store.objects.all().delete()
            Inventory.objects.all().delete()
            Order.objects.all().delete()
            OrderItem.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Data cleared'))

        self.stdout.write(self.style.SUCCESS('Seeding categories...'))
        categories = []
        category_names = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports', 'Toys', 'Beauty']

        for name in category_names:
            cat, created = Category.objects.get_or_create(
                name=name,
                defaults={}
            )
            categories.append(cat)
            if created:
                self.stdout.write(f'  Created category: {name}')

        self.stdout.write(self.style.SUCCESS('Seeding products...'))
        products = []
        for category in categories:
            for i in range(5):
                product_title = f'{category.name} Product {i+1} - {fake.word()}'
                product, created = Product.objects.get_or_create(
                    title=product_title,
                    category=category,
                    defaults={
                        'description': fake.paragraph(nb_sentences=3),
                        'price': round(random.uniform(10, 500), 2),
                    }
                )
                products.append(product)
                if created:
                    self.stdout.write(f'  Created product: {product_title}')

        self.stdout.write(self.style.SUCCESS('Seeding stores...'))
        stores = []
        for i in range(5):
            store_name = f'Store {i+1} - {fake.city()}'
            store, created = Store.objects.get_or_create(
                name=store_name,
                defaults={
                    'location': fake.address(),
                }
            )
            stores.append(store)
            if created:
                self.stdout.write(f'  Created store: {store_name}')

        self.stdout.write(self.style.SUCCESS('Seeding inventory...'))
        for store in stores:
            for product in products:
                inventory, created = Inventory.objects.get_or_create(
                    store=store,
                    product=product,
                    defaults={
                        'quantity': random.randint(0, 100),
                    }
                )
                if created:
                    self.stdout.write(f'  Created inventory: {product.title} at {store.name}')

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
