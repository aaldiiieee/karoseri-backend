# Karoseri Component Damage Classification

This is a FastAPI project for the final project of Pamulang University (UNPAM)

## Quick Start (Automation Scripts)

### 1. Setup Environment
Run the setup script to create the virtual environment and install all dependencies:
```bash
./setup.sh
```

### 2. Running the Application
Use the run script to start the server.

**Development Mode (with auto-reload):**
```bash
./run.sh --dev
```

**Production Mode:**
```bash
./run.sh --prod
```

## Manual Installation Guide (Alternative)

1. **Clone this repository**:
    ```bash
    git clone https://github.com/aaldiiieee/karoseri-component-damage-classification.git
    cd karoseri-component-damage-classification
    ```

2. **Create a Virtual Environment (VENV)**:
   ```bash
   python3 -m venv .venv
   ```

3. **Activate the Virtual Environment**:
   - **macOS/Linux**: `source .venv/bin/activate`
   - **Windows**: `.venv\Scripts\activate`

4. **Install Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Running the Application Manually

Start the server using uvicorn:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Once running, you can access:
- **Application**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **API Documentation (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
