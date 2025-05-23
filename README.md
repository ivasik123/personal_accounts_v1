# personal_accounts

# Документация

## Общее описание
Проект представляет собой образовательную платформу с пользователями разных ролей (студенты, преподаватели, администраторы), курсами и подписками на курсы. Система включает:
- Аутентификацию и авторизацию пользователей
- Управление курсами и подписками
- Отслеживание активности пользователей
- Административную панель с расширенными возможностями

## Модели (models.py)

### UserProfile
Кастомная модель пользователя, расширяющая AbstractBaseUser.

**Поля:**
- `email` - уникальный email пользователя (используется как USERNAME_FIELD)
- `username` - имя пользователя
- `contacts` - контактная информация
- `notifications` - настройки уведомлений
- `date_joined` - дата регистрации
- `last_login` - время последнего входа
- `role` - роль пользователя (student/teacher/admin)
- `is_active` - активен ли аккаунт
- `is_staff` - является ли сотрудником
- `last_activity` - время последней активности
- `last_admin_access` - время последнего доступа в админку

**Методы:**
- `clean()` - валидация роли пользователя
- `__str__()` - строковое представление (email)

### UserProfileManager
Кастомный менеджер пользователей с методами:
- `create_user()` - создание обычного пользователя
- `create_superuser()` - создание суперпользователя
- `update_activity()` - обновление времени активности

### Course
Модель курса.

**Поля:**
- `title` - название курса
- `description` - описание
- `teachers` - преподаватели (ManyToMany с UserProfile)
- `start_date`, `end_date` - даты начала и окончания
- `is_active` - активен ли курс

### Subscription
Модель подписки студента на курс.

**Поля:**
- `student` - студент (ForeignKey к UserProfile)
- `course` - курс (ForeignKey к Course)
- `date_subscribed` - дата подписки
- `is_active` - активна ли подписка

## Представления (views.py)

### Основные функции:
- `user_login()` - аутентификация пользователя
- `profile()` - просмотр профиля
- `user_logout()` - выход из системы
- `subscribe_to_course()` - подписка на курс
- `unsubscribe_from_course()` - отмена подписки
- `student_register()` - регистрация студента

### Административные функции:
- `user_activity_report()` - отчет по активности пользователей (только для суперпользователей)

## Административная панель (admin.py)

### UserProfileAdmin
Кастомная админка для UserProfile с:
- Отображением email, username, роли, статусов и времени активности
- Фильтрацией по роли, активности и статусу staff
- Read-only полями для времени активности
- Кастомным queryset, ограничивающим доступ к данным staff-пользователей
- Действием для деактивации неактивных пользователей

### CourseAdmin
Админка для курсов с:
- Отображением названия, дат, активности и списка преподавателей
- Inline-отображением подписок
- Фильтрацией по активности и дате начала

### SubscriptionAdmin
Админка для подписок с:
- Отображением студента, курса, даты подписки и активности
- Фильтрацией по активности и курсу
- Иерархией по дате подписки

## Middleware (middleware.py)

### UserActivityMiddleware
Отслеживает активность пользователей и обновляет поле `last_activity` при каждом запросе аутентифицированного пользователя.

### AdminAccessMiddleware
Отслеживает доступы в админку и обновляет поле `last_admin_access`, а также логирует такие события.

## Особенности реализации
1. Кастомная модель пользователя с расширенными полями
2. Отслеживание активности пользователей через middleware
3. Разграничение прав доступа в админке
4. Гибкая система подписок на курсы
5. Автоматическая деактивация неактивных пользователей
