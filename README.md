# Backend Optimization
This project is a Django-based web application that manages subscription services for clients. 
It includes endpoints to manage subscriptions, calculate total prices, track the status of active subscriptions and more. 
The project also utilizes Celery for background tasks and Redis for task queuing, along with caching mechanisms to optimize performance.

# Features
Subscription Management: A REST API that allows listing subscriptions, calculating total price, and fetching information on active subscriptions.
Caching: Price calculations are cached for faster access, and cache invalidation is done whenever necessary.
Background Tasks: Price and comment updates are handled asynchronously using Celery and workers.
PostgreSQL Database: The application uses PostgreSQL as the database backend for storing subscription information.
Redis: Redis is used as a broker for Celery tasks.
Tests: 90%+ code coverage
Optimization of sql queries: caching, indexes, annotations and aggregations...
Docker: for easy configuration.

# Technologies
Django
Django Rest Framework
Postgresql
Docker
Redis
Celery
Python
Coverage
Flower

# Set-UP
(bash) git clone https://github.com/Qermon/backend.git or use get from Version Control
Add .env file in project root folder(service)
In .env write your SECRET_KEY(Example: SECRET_KEY=123)
(bash) docker-compose up --build
