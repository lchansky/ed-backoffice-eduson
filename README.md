# Simba (Backoffice Eduson)

### 4 раздела: удостоверения об образовании, проверка фида, промокоды, интеграция сводной таблицы с notion

### Деплой:  
Настраиваем config:set в dokku и пушим в ветку dokku  
Либо локально запускаем docker-compose-dev.yml. Сайт будет доступен на `localhost:80`  
После деплоя доступен на https://simba.vs2.srv.eduson.tv

Кроме всего прочего, при деплое этого приложения мы сделали следующее:
1. Сделал один и тот же Dockerfile для django_gunicorn (web), 
celery_beat (service_1) и worker (service_2).
2. Сформировали Procfile:
    ```
    web: sh /entrypoint.sh
    service_1: command
    service_2: command
    ```
3. Прописали команду в Dokku:
    ```
   ps:scale lead-rescuer service_1=1 service_2=2
   ```
   После указания этой команды, при каждом деплое приложения, будут 
подниматься указанные сервисы.
4. После первого деплоя, нужно создать в админке периодическую задачу по обновлению сводной.

##### Env переменные (для локального запуска сохранить .env рядом с docker-compose-dev.yml:
```
SECRET_KEY=django_secret_key
SUPER_USER_NAME=admin
SUPER_USER_PASSWORD=password
SUPER_USER_EMAIL=admin@eduson.tv

POSTGRES_HOST=
POSTGRES_PORT=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=

TG_TOKEN=
TG_CHAT_ID=
TG_INTEGRATIONS_CHAT_ID=

NOTION_TOKEN=
NOTION_COURSES_DATABASE_ID=
NOTION_CATEGORIES_DATABASE_ID=
NOTION_CATEGORY_POPULAR_COURSES_PAGE_ID=
NOTION_LANDINGS_DATABASE_ID=
CELERY_BROKER_URL=

MIXPANEL_TOKEN=
```