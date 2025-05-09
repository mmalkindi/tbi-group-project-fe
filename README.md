# TBing Search

> Muhamad Rifqi - `2206081433`  
> Muhammad Milian Alkindi - `2206081856`  
> Fatih Raditya Pratama - `2206083520`

## Local Installation Procedure

1. Install required libraries

    ```bash
    pip install -r requirements.txt
    ```

2. Create a `.env` file in the root directory with the following content:

    ```env
    SEARCH_HOST=http://localhost:9200  ## Change this to your Elasticsearch host
    DJANGO_SECRET_KEY="insert-django-secret-key-here"

    DEBUG_ENABLED=True
    IS_PRODUCTION=False
    ```

3. Run server

    ```bash
    python manage.py runserver
    ```

4. Open your browser and navigate to `http://localhost:8000` to access the application.
