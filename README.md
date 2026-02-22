# URL Shortener

A functional, asynchronous URL shortening service built as a learning project to explore modern backend infrastructure, containerization, and monitoring. 

## 🎯 Project Goals & Features
Instead of just building a basic CRUD app, this project focuses on production-like practices:
* **Asynchronous API:** Built with FastAPI and `asyncpg` for non-blocking database operations.
* **Caching & Rate Limiting:** Uses Redis to cache hot links and protect the API from spam (10 req/min per IP).
* **Containerization:** Packaged using multi-stage Docker builds to keep the image lightweight and secure.
* **Observability:** Integrated Prometheus to scrape internal metrics and Grafana to visualize traffic and latency.

## 🛠️ Tech Stack
* **Backend:** Python 3.13+, FastAPI, Uvicorn
* **Data:** PostgreSQL, Redis
* **DevOps & Monitoring:** Docker, Nginx, Prometheus, Grafana

## 🚀 Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Barden-dev/URLShortener.git
   cd URLShortener
   ```
   
2. **Environment Variables:**
   Rename `.env.example` to `.env` and fill in your local credentials for Postgres and Redis. By default the domain is `localhost`, you can change it for example to `example.com`

3. **Run with Docker:**
   ```bash
   docker compose up -d --build 
   ```
   
* The API will be available at `http://localhost:8080`. The Grafana dashboard is routed through Nginx at `/grafana/`.

## 🔌 API Usage

Full interactive documentation (Swagger UI) is automatically generated and available at `/docs` once the application is running. Here is a quick overview of the main endpoints:

### 1. Create a Short Link
**`POST /shorten`**
Expects a JSON payload with the destination URL.
* **Request:** 
    ```json
    {"target_url": "https://www.google.com"}
    ```

* **Response:** 
    ```json
    {"target_url": "https://www.google.com/", "secret_key": "XyZ123ab", "is_active": true, "clicks": 0}
    ```
### 2. Use the Short Link

**`GET /{secret_key}`**
* Navigating to this URL performs an HTTP redirect to the original destination.
* *Note: The click counter is incremented asynchronously in the background so the redirect happens instantly.*

### 3. Check Statistics

**`GET /stats/{secret_key}`**
Returns the original URL and the total number of times the short link was accessed.

* **Response:** 
    ```json
    {"target_url": "https://www.google.com/", "clicks": 42}
    ```