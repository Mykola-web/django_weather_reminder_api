from django.core.management.base import BaseCommand

from api.models import CustomUser, Subscription

class Command(BaseCommand):
    help = "Command to quickly make certain amount of users"

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type = int,
            default = 5,
            help='Count users to make, default = 5, command example : py manage.py fake_data_maker --count 15 '
        )

    def handle(self, *args, **options):
        users_to_make = options['count']
        for i in range(users_to_make):
            if not CustomUser.objects.filter(username = f'tester{users_to_make}'):
                new_user = CustomUser.objects.create_user(username = f'tester{users_to_make}',
                                                          email = f"test{users_to_make}@example.com",
                                                          password = '12345678')
                Subscription.objects.create(user = new_user, city ='london')

        print("Users in database:", CustomUser.objects.count())