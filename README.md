# FastAPI Backend

## Project Structure

```
fastapi/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   └── __init__.py
│   ├── core/
│   │   └── __init__.py
│   ├── models/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   ├── dependencies/
│   │   └── __init__.py
│   └── static/
│       └── .gitkeep
├── main.py
├── Pipfile
└── README.md
```

## Prerequisites

Make sure you have pipenv installed:
```bash
pip install pipenv
```

## How to Run

1. Install dependencies:
   ```bash
   pipenv install
   ```

2. **Development mode** (with auto-reload):
   ```bash
   pipenv run dev
   ```

3. **Production mode**:
   ```bash
   pipenv run prod
   ```

4. Visit [http://localhost:8000](http://localhost:8000) in your browser.

## Alternative: Manual Commands

If you prefer to run commands manually:

1. Activate the virtual environment:
   ```bash
   pipenv shell
   ```

2. Start the development server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. Or start production server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## Description
- `main.py`: Entry point for the FastAPI app.
- `Pipfile`: Dependency management file for pipenv with scripts.
- `app/`: Application code and modules.
  - `api/`: API route definitions.
  - `core/`: Core settings, configuration, and utilities.
  - `models/`: Database models.
  - `schemas/`: Pydantic schemas for data validation.
  - `services/`: Business logic and service layer.
  - `dependencies/`: Dependency injection modules.
  - `static/`: Directory for React build files (served at `/static`).

## Adding Dependencies

To add new packages:
```bash
pipenv install package-name
```

To add development dependencies:
```bash
pipenv install --dev package-name
```

## Scripts

- `pipenv run dev`: Runs the server in development mode with auto-reload
- `pipenv run prod`: Runs the server in production mode 