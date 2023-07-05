# Backoffice Eduson

### Пока что есть одна функция - ускорение работы с удостоверениями об образовании

### Деплой:  
Просто заполняем env файл и пушим в ветку dokku  
Либо локально запускаем docker-compose.yml. Сайт будет доступен на `localhost:80`  
После деплоя доступен на https://backoffice-eduson.srv1.testla.app/

##### Env файл:
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
```