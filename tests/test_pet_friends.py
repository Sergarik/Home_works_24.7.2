import os
from api import PetFriends
from settings import (valid_email, valid_password, invalid_email, invalid_password)


pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем, что запрос api ключа возвращает статус 200 и
        в результате содержится слово key"""
    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем, что запрос списка всех питомцев возвращает не пустой список. Для этого сначала получаем
        Api ключ и сохраняем в переменную auth_key. Далее, используя этот ключ, запрашиваем список всех питомцев и
        проверяем, что список не пустой. Доступное значение параметра filter - 'my_pets', либо всех питомцев '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    # Сверяем полученные данные
    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Тёма', animal_type='Енот', age='2',
    pet_photo='image/Prikol_Enot.jpg'):
    """ Проверяем, что запрос на добавление нового питомца
        с указанными параметрами выполняется успешно."""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученные данные
    assert status == 200
    assert result['name'] == name
    assert result['animal_type'] == animal_type



def test_add_new_pet_with_invalid_data_age(name='Шарик', animal_type='Собака', age='-1',
    pet_photo='image/Sobakin.jpg'):
    """ Проверяем, что запрос на добавление нового питомца
        с отрицательным возрастом выполняется """

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученные данные
    assert status == 200
    assert 'name' in result

def test_get_api_key_for_invalid_email_and_password(email = invalid_email, password = invalid_password):
    """ Проверяем, что запрос api ключа с неверным email пользователя
        возвращает статус 403 и в результате не содержится слово key"""
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'key' not in result

def test_get_all_pets_with_invalid_authkey(filter=''):
    """ Проверяем что запрос всех питомцев с невалидным токеном возвращает 403 ошибку.
    Сначала получаем api ключ и сохраняем в переменную auth_key. Далее изменяем этот ключ
    запрашиваем список всех питомцев и проверяем что нам возвращается."""

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Полученный токен переворачиваем
    auth_key['key'] = auth_key.pop('key')[::-1]

    # Список всех питомцев
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 403

def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и
    # в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in [pet['id'] for pet in my_pets['pets']]


def test_successful_update_self_pet_info(name="Туз", animal_type="Собака", age=3):
    """ Проверяем возможность обновления информации о питомце"""

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if not my_pets['pets']:
        raise Exception("There is no my pets")
    pet_id = my_pets['pets'][0]['id']

    status, result = pf.update_pet_info(auth_key, pet_id, name, animal_type, age)

    # Проверяем что статус ответа = 200 и атрибуты питомца поменялись
    assert status == 200
    assert result['name'] == name
    assert result['animal_type'] == animal_type
    assert result['age'] == str(age)


def test_rejection_update_self_pet_info_without_name(name='', animal_type="Собака", age=5):
    """ Проверяем невозможность очистить имя питомца
        путём передачи пустого поля name """

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if not my_pets['pets']:
        raise Exception("There is no my pets")
    pet_id = my_pets['pets'][0]['id']

    status, result = pf.update_pet_info(auth_key, pet_id, name, animal_type, age)


    # Проверяем что статус ответа = 200 и имя питомца не стало пустым
    assert status == 200
    assert result['name']


def test_rejection_update_self_pet_info_without_animal_type(name="Жора", animal_type='', age= 1):
    """ Проверяем невозможность очистить типа питомца путём
        передачи пустого поля animal_type """

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if not my_pets['pets']:
        raise Exception("There is no my pets")
    pet_id = my_pets['pets'][0]['id']

    status, result = pf.update_pet_info(auth_key, pet_id, name, animal_type, age)

    # Проверяем что статус ответа = 200 и тип питомца не пустой
    assert status == 200
    assert result['animal_type']


def test_add_new_pet_with_incorrect_data_without_foto(name='tESTo', animal_type='', age=''):
    """ Проверяем, что запрос на добавление нового питомца без фото с некорректно указанным именем
        набор букв, animal_type и age - пустые. Выполняется ли успешно."""

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)


    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name

def test_add_new_photo(pet_photo='image/cat.jpg'):
    """Проверяем что можно добавить фото питомца к питомцу без фото"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet_without_photo(auth_key, "Стрелка", "Собака", "4")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на добавление фото
    pet_id = my_pets['pets'][-1]['id']
    status, result = pf.add_pet_photo(auth_key, pet_id, pet_photo)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем статус ответа 200 в списке питомцев имя нашего обновляемого питомца
    assert status == 200
    assert result['name'] == my_pets['pets'][0]['name']

def test_update_self_pet_info_with_invalid_pet_id(name='Жека', animal_type='Кот', age=7, pet_photo='image/cat.jpg'):

    """Проверяем возможность обновления информации о питомце с невалидным id"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст c обратным id
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'][::-1], name, animal_type, age)

        # Проверяем что статус ответа = 400
        assert status == 400
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")

def test_successful_update_pet_info_cat(name='Малыш', animal_type='cat', age='1'):
    """Проверяем запрос на изменение данных питомца"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')


    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        assert status == 200
        assert result['name'] == name
    else:
        raise Exception("There is no my pets")

def test_unsuccessful_add_photo_png_format(pet_photo='image/cat-png.png'):
    """Проверяем что нельзя добавить фото животного в формате .png"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, filter="my_pets")

    if len(my_pets['pets']) == 0:
        pf.add_new_pet_without_photo(auth_key, name='Мерча', animal_type='cat', age='2')
        _, my_pets = pf.get_list_of_pets(auth_key, filter="my_pets")

    pet_id = my_pets['pets'][0]['id']
    status, result = pf.add_pet_photo(auth_key, pet_id, pet_photo)

    assert status != 200