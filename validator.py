import re


def validate_user_data(name, email, repo):
    errors = []
    
    # 1. Проверка на пустые поля
    if not name:
        errors.append("Имя обязательно для заполнения")
    if not email:
        errors.append("Email обязателен для заполнения")
    
    # 2. Проверка длины имени
    if name and len(name) < 5:
        errors.append("Имя должно содержать минимум 5 символов")
    
    # 3. Проверка формата email
    if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        errors.append("Email должен быть в формате example@domain.com")
    
    # 4. Проверка уникальности email
    if email and any(user['email'] == email for user in repo.get_content()):
        errors.append("Пользователь с таким email уже существует")
    
    return errors