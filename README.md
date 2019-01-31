Django comments
====================================
Зависимости:
* Python 3.6
* django предоставляет удобную работу с разнородными сущностями (ContentType)
* django-rest-framework позволяет быстро и легко реализовывать REST-стиль
* django-mptt для ускорения работы с деревом комментариев за счет отказа от рекурсивных запросов
* celery для работы с асинхронными задачами
* django-channels для работы с веб-сокетами
* Daphne asgi веб-сервер
* PostgreSQL
* Redis используется в качестве брокера сообщений celery

Запуск
-----------
1. Установить docker
2. Установить docker-compose
3. Клонировать этот репозиторий
4. Запустить команду в месте расположения файла docker-compose.yml
```bash
docker-compose up --build
```     
или, при отсутствии у пользователя прав,
```bash
sudo docker-compose up --build
```
Если с первого раза контейнер не запустится, в логах будет ошибка запуска апи - не отвечала база из-за залития дампа,
нужно перезапустить контейнер.
```bash
docker-compose up
```
или
```bash
sudo docker-compose up
```
5. Поверить доступнось приложения. Если запуск прошел успешно, GET запрос на http://localhost:8000/health должен вернуть
код 200_OK.

### Тестовые данные
Бэкап базы с тестовыми данными заливается при первом старте контейнера postgres.
Тестовые данные содержат в себе по 1 сущности блога и топика с предсозданными комментариями, а так же пользователя
```bash
user_id: 1
username: super_admin
```

Структура
-----------
В запросах на методы модификации данных должен содержатсья параметр auth_user (эмуляция авторизации). По умолчанию
работает limit-offst пагинация.
Все примеры запросов работают для тестового дампа БД.

### Cущности контента
Блоги
```bash
curl -X GET \
  http://localhost:8000/content/blogs
```
Топики
```bash
curl -X GET \
  http://localhost:8000/content/topics
```
### Комменатрии
Получение комментариев 1го уровня для сущности. 
Формат ответа сущности комментария.
```python
{
    "id": 20020,  # идентификатор комментария
    "content_type": 12, # тип сущности родителя
    "object_id": 1,  # идентификатор в рамках сущности родителя
    "text": "Approach style let mission property",
    "parent": null,  # идентификатор родительского комментария
    "user": {
        "id": 1,
        "username": "super_admin"
    },
    "created_at": "2019-01-31T05:15:14.283002Z",
    "updated_at": "2019-01-31T05:15:14.283043Z",
    "self_content_type": 7  # тип текущей сущности (для сущностей с возможностью комментирования)
}
```
```bash
curl -X GET \
  'http://localhost:8000/comments?content_type=11&object_id=1'
```
Получение комментариев 1го уровня для комментария.
```bash
curl -X GET \
  'http://localhost:8000/comments?parent=1'
```
Получение дочернних комментариев по родительскому. Обработка на фронте осуществляется за счет 
сортировки в рамках дерева и наличия идентификатора родительского комментария.
```bash
curl -X GET \
  'http://localhost:8000/comments?parent=1&children=true'
```
Получение дочерних комментариев для заданной сущности комментария.
```bash
curl -X GET \
  'http://localhost:8000/comments?content_type=7&object_id=1&children=true'
```
Получение списка комментариев для пользователя.
```bash
curl -X GET \
  'http://localhost:8000/comments?user=1'
```
Создание комментария.
```bash
curl -X POST \
  http://localhost:8000/comments \
  -H 'Content-Type: application/json' \
  -d '{
	"auth_user": 1,
	"content_type": 11,
	"object_id": 1,
	"text": "test 1"
}'
```
Создание комментария на комментарий.
```bash
curl -X POST \
  http://localhost:8000/comments \
  -H 'cache-control: no-cache' \
  -d '{
    "auth_user": 1,
    "content_type": 7,
    "object_id": 20021,
    "text": "test 2"
}'
```
Удаление комментария.
```bash
curl -X DELETE \
  http://localhost:8000/comments/20022 \
  -H 'Content-Type: application/json' \
  -d '{
    "auth_user": 1
}'
```
Редактирование комментария.
```bash
curl -X PATCH \
  http://localhost:8000/comments/20021 \
  -H 'Content-Type: application/json' \
  -d '{
    "auth_user": 1,
    "text": "test patch"
}'
```
Просмотр истории изменения комментария.
```bash
curl -X GET \
  http://localhost:8000/comments/history/20021
```
### Выгрузка комментариев
Заказ отчета. Генерация происходит в фоне.
```bash
curl -X POST \
  http://localhost:8000/comments/reports \
  -H 'Content-Type: application/json' \
  -d '{
	"auth_user": 1,
	"user": 1,
	"content_type": 11,
	"object_id": 1,
	"created_at__gte": "2019-01-01T10:10:10.776244Z",
	"created_at__lt": "2019-02-28T10:10:10.776244Z"
}'
```
```json
{
    "id": 1,
    "created_by": 1,
    "status": "pending",
    "created_at": "2019-01-31T14:54:50.022164Z",
    "updated_at": "2019-01-31T14:54:50.022216Z",
    "user": 1,
    "content_type": 11,
    "object_id": 1,
    "created_at__gte": "2019-01-01T10:10:10.776244Z",
    "created_at__lt": "2019-02-28T10:10:10.776244Z"
}
```
Получение статуса выполнения.
```bash
curl -X GET \
  http://localhost:8000/comments/reports/1
```
```json
{
    "id": 1,
    "created_by": 1,
    "status": "finished",
    "created_at": "2019-01-31T14:54:50.022164Z",
    "updated_at": "2019-01-31T14:54:50.388387Z",
    "user": 1,
    "content_type": 11,
    "object_id": 1,
    "created_at__gte": "2019-01-01T10:10:10.776244Z",
    "created_at__lt": "2019-02-28T10:10:10.776244Z"
}
```
Скачивание отчета. Скачивание доступно для отчетов в статусе finished. Поддержка различных форматов
осуществляется путем сопоставления рендер-класса и формата, формат подставляется из строки запроса. 
Данные для отчета к этому моменту лежат в базе в формате JSON.
```bash
curl -X GET \
  http://localhost:8000/comments/reports/1/xml
```
```bash
curl -X GET \
  http://localhost:8000/comments/reports/1/json
```
### Подписка на комментарии к сущности
```bash
curl -X POST \
  http://localhost:8000/comments/subscribe \
  -H 'Content-Type: application/json' \
  -d '{
	"auth_user": 1,
	"content_type": 12,
	"object_id": 1
}'
```
### Оповещение об изменениях (веб-сокеты)
Оповещения для пользователя приходят в сокет ws://localhost:8000/ws/push/{user_id}/
На локальной машине нужно открыть страницу push.html, в ней, для примера, добавлено отображение
сообщений для user_id=1. 
