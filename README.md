I see the correction you're pointing out regarding the Celery app. Below is the updated version of the `README.md` to reflect the correct command and context for running the tasks.

---

## **Project: Nex-Probe Web Scraper**

### **Overview**

This project is a modular, scalable web scraping system built using:

- **Scrapy**: For scraping content from different websites.
- **Celery**: For managing background tasks such as scraping tasks, scheduled with **Celery Beat**.
- **Redis**: As the broker for Celery tasks.
- **Elasticsearch**: For storing and searching the scraped content.
- **Docker**: For containerizing the entire setup, making it easy to run in any environment.
- **Selenium** (Optional): Used in some spiders to handle dynamic content with JavaScript.

---

### **Project Structure**

```bash
nex-probe/
│
├── celery_app.py               # Celery application initialization
├── Dockerfile.dev               # Dockerfile for development
├── docker-compose.dev.yml       # Docker Compose setup for development
├── requirements.txt             # Python dependencies
├── go-spider.py                 # Optional script to trigger scrapers manually
├── scrapy.cfg                   # Scrapy configuration file
├── logs/                        # Directory for logs (can be used for custom logs)
├── scraper/                     # Main Scraper directory
│   ├── __init__.py              # Scraper module initialization
│   ├── items.py                 # Scrapy items definition
│   ├── middlewares.py           # Scrapy middlewares
│   ├── pipelines.py             # Scrapy pipelines (to store scraped data)
│   ├── settings.py              # Scrapy settings
│   ├── tasks.py                 # Celery tasks for scraping
│   ├── utils.py                 # Utility functions for spiders
│   ├── user_agents.txt          # List of random user agents
│   ├── spiders/                 # Directory for spiders
│   │   ├── __init__.py          # Spiders module initialization
│   │   ├── aggressive_spider.py # Spider for aggressively scraping a site
│   │   └── news_spider.py       # Spider to scrape news content
└── .env                         # Environment variables file
```

### **Components & Tools**

- **Scrapy**: Scraping framework used for crawling web content.
- **Celery**: Distributed task queue to run tasks asynchronously. This project uses Celery to trigger Scrapy spiders.
- **Redis**: Message broker for Celery.
- **Elasticsearch**: Stores scraped content for fast searching and querying.
- **Docker**: Containerizes all the components to run them easily on different systems.
- **Selenium**: (Optional) To handle dynamic content that requires JavaScript execution.

---

### **Setting Up the Project**

#### **Step 1: Clone the Repository**

```bash
git clone https://github.com/yourusername/nex-probe.git
cd nex-probe
```

#### **Step 2: Setup Environment Variables**

Create a `.env` file in the root directory. Add any environment-specific settings here, such as Redis connection settings, Elasticsearch credentials, etc. Example:

```
REDIS_URL=redis://redis:6379/0
ELASTICSEARCH_HOST=elasticsearch
LOG_LEVEL=DEBUG
```

#### **Step 3: Build and Run Docker Containers**

Make sure Docker is installed on your system. To build and start all services (Scrapy, Celery, Redis, Elasticsearch), run the following command:

```bash
docker compose -f docker-compose.dev.yml up --build
```

This will:

- Build and start the containers for Redis, Elasticsearch, Scrapy, Celery Workers, and Celery Beat.
- Scrapy spiders will be triggered by Celery tasks.

---

### **Running the Scrapers**

The scraping tasks are set up to run periodically using **Celery Beat**. You can also manually trigger the scrapers.

#### **Celery Commands**

You can use the following commands to manage Celery and its workers:

1. **Starting the Celery Worker:**

   - This will start the worker that listens to tasks in the queue.

   ```bash
   celery -A celery_app worker --loglevel=info
   ```

2. **Starting Celery Beat:**

   - This will schedule periodic tasks defined in `celery_app.py`.

   ```bash
   celery -A celery_app beat --loglevel=info
   ```

3. **Manually Trigger a Task:**

   - Inside the running container (e.g., `celery_worker_1`), you can manually trigger a task:

   ```bash
   docker exec -it celery_worker_1 bash
   celery -A celery_app call scraper.tasks.scrape_news
   ```

---

### **How the Project is Set Up**

#### **1. Scrapy Setup**

Scrapy spiders are located in the `scraper/spiders/` directory. You can define multiple spiders here. For instance, the `news_spider.py` scrapes articles from a news website.

The settings for Scrapy are located in `scraper/settings.py`. This file defines settings such as:

- User agents rotation
- Pipelines to store scraped data in Elasticsearch
- Middleware for retrying requests

#### **2. Celery Setup**

`celery_app.py` in the root directory is where the Celery app is initialized. It uses Redis as a broker and includes tasks from `scraper.tasks`.

Example of `celery_app.py`:

```python
from celery import Celery
from celery.schedules import crontab

app = Celery('nex-probe', broker='redis://redis:6379/0')

app.conf.beat_schedule = {
    'run-scrape-every-15-minutes': {
        'task': 'scraper.tasks.scrape_news',
        'schedule': crontab(minute='*/15'),  # every 15 minutes
    },
}
app.conf.timezone = 'UTC'
```

#### **3. Celery Tasks**

The Celery tasks are defined in `scraper/tasks.py`. Example task:

```python
from celery_app import app

@app.task
def scrape_news():
    # Add your scraping logic here
    print("Scraping news website...")
```

#### **4. Docker Compose**

The `docker-compose.dev.yml` file defines the services (Redis, Elasticsearch, Celery, Scrapy) and their interdependencies. Each component runs in its own container.

Here’s an overview of the services defined:

- **Redis**: Acts as the broker for Celery tasks.
- **Elasticsearch**: Stores the scraped data.
- **Celery Workers**: Process tasks queued by Celery.
- **Celery Beat**: Periodically schedules tasks like scraping jobs.
- **Scrapy**: Runs the spiders inside the Celery tasks.

---

### **Key Commands**

- **Build and Start All Services**:

  ```bash
  docker compose -f docker-compose.dev.yml up --build
  ```

- **Manually Trigger a Task (Inside the Celery Worker Container)**:

  ```bash
  docker exec -it celery_worker_1 bash
  celery -A celery_app call scraper.tasks.scrape_news
  ```

- **Check Logs of Celery Worker**:
  ```bash
  docker logs celery_worker_1
  ```

---

### **Known Issues and Troubleshooting**

- **Task Not Running**: Ensure that the task is registered in Celery by checking the worker logs (`docker logs celery_worker_1`). If tasks aren't being picked up, ensure that Redis is running and connected.
- **No Data in Elasticsearch**: Make sure the Elasticsearch service is running and check the pipelines in Scrapy to ensure data is being saved.
- **Browser Automation (Selenium)**: If you are using Selenium for scraping dynamic content, ensure that the `chromedriver` and `selenium` are properly configured in the spider.

---

### **Future Enhancements**

- Add more spiders for different CMS (e.g., WordPress, Drupal).
- Implement automatic retry mechanisms for failed scrapes.
- Improve logging to include more detailed task-level logs.

---

This guide covers the full setup of the project along with how to run and troubleshoot the system. The corrected command for manually triggering a task using Celery is:

```bash
celery -A celery_app call scraper.tasks.scrape_news
```

Make sure everything is correctly configured, especially Celery and Scrapy, to ensure smooth operation across containers.
