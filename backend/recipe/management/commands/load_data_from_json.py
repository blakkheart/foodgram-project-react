import json
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.db.utils import IntegrityError

from recipe.models import Ingredient, Tag

User = get_user_model()

list_of_data = [
    'ingredients',
    'tags',
    'users',
]

data_models_dict = {
    'ingredients': Ingredient,
    'tags': Tag,
    'users': User,
}


class Command(BaseCommand):
    """Менеджмент команда для выгрузки данных из json."""

    def handle(self, *args: Any, **options: Any) -> None:
        for data_file_name in list_of_data:
            print(f'loading {data_file_name}', end='')
            with open(
                str(settings.DB_DATA_DIR) + '/' + data_file_name + '.json',
                encoding='utf-8',
            ) as file:
                for model_data in json.load(file):
                    try:
                        model = data_models_dict.get(data_file_name)(
                            **model_data
                        )
                        model.save()
                        print('...', end='')
                    except IntegrityError:
                        continue
            print('..Done!')
