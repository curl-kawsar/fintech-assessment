## Setup and Startup

### 1. Clone the Repository

```bash
git clone https://github.com/curl-kawsar/fintech-assessment.git
```

After cloning, go inside the project folder:

```bash
cd fintech-assessment
```

## Run with PostgreSQL and Redis

Use Docker only for PostgreSQL and Redis. Run Django and Celery from the terminal.

### 2. Start PostgreSQL and Redis

```bash
docker compose -f docker-compose.infra.yml up -d
```

Services will run on:

```text
PostgreSQL: localhost:5432
Redis: localhost:6380
```

---

### 3. Create Virtual Environment and Install Dependencies

#### Windows

```powershell
python -m venv venv
.\venv\Scripts\pip.exe install -r requirements.txt
copy .env.example .env
```

#### macOS/Linux

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

---

### 4. Run Database Migration

#### Windows

```powershell
.\venv\Scripts\python.exe manage.py migrate
```

#### macOS/Linux

```bash
python manage.py migrate
```

---

### 5. Start Django API

#### Windows

```powershell
.\venv\Scripts\python.exe manage.py runserver
```

#### macOS/Linux

```bash
python manage.py runserver
```

The API will be available at:

```text
http://localhost:8000
```

For Postman-style request/response examples, see [API_TESTING.md](API_TESTING.md).

---

### 6. Start Celery Worker

Open another terminal inside the same project folder.

#### Windows

```powershell
.\venv\Scripts\celery.exe -A myproject worker --loglevel=info --pool=solo
```

#### macOS/Linux

```bash
celery -A myproject worker --loglevel=info
```

> On Windows, `--pool=solo` is required.

---

### 7. Run Tests

#### Windows

```powershell
.\venv\Scripts\pytest.exe
```

#### macOS/Linux

```bash
pytest
```

---

### 8. Stop PostgreSQL and Redis

```bash
docker compose -f docker-compose.infra.yml down
```
