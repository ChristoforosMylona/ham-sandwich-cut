## Clone the Repository

If you haven't already, clone the repository to your local machine:

```bash
git clone https://github.com/ChristoforosMylona/ham-sandwich-cut.git
cd src
```

---

## Running Locally with Docker

To run this project locally with Docker, follow the steps below:

### Prerequisites
Make sure you have the following installed:
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Steps to Run the Project Locally

1. **Build and Start the Containers**
   From the root of the project, run the following command to build the Docker images and start the containers:
   
   ```bash
   docker-compose up --build
   ```
   
   This command will:
   - Build the frontend and backend Docker images.
   - Start the Flask backend on `http://localhost:5000`.
   - Start the React frontend on `http://localhost:5173`.

2. **Access the Application**
   Once the containers are up, you can access the following:
   - **Frontend (React + Vite)**: Open your browser and go to [http://localhost:5173](http://localhost:5173).
   - **Backend (Flask)**: The API will be available at [http://localhost:5000](http://localhost:5000).

3. **Stopping the Containers**
   When you're done working with the app, you can stop the containers by running:
   
   ```bash
   docker-compose down
   ```

### Troubleshooting

- If you're running into issues with outdated code or images, you can force a fresh rebuild by running:
  
  ```bash
  docker-compose up --build --force-recreate
  ```
  
- To clear old containers and images:
  
  ```bash
  docker-compose down --rmi all --volumes --remove-orphans
  docker-compose up --build
  ```

---

## Running Locally in Development Mode (with Script)

If you'd like to run the project locally in development mode (using the provided shell script), follow the instructions below. This method is for local development only and **should not be used for production**.

### Prerequisites
Make sure you have the following installed:
- [Node.js](https://nodejs.org/) (for the React frontend)
- [Python](https://www.python.org/downloads/) (version 3.6 or higher, for Flask)
- [pip](https://pip.pypa.io/en/stable/installation/) (for Python package management)

Additionally, you will need a **virtual environment** for Python dependencies.

### Steps to Run the Project Locally in Development Mode

1. **Set Up Python Virtual Environment (for Flask)**
   Navigate to the `flask_backend` directory and create a virtual environment:
   
   ```bash
   cd flask_backend
   python3 -m venv venv
   ```

2. **Install Flask Dependencies**
   With the virtual environment activated, install the required Python packages:
   
   ```bash
   source venv/bin/activate  # For Linux/macOS
   # OR
   source venv/Scripts/activate  # For Windows
   cd ham_sandwich_cuts
   pip install -r requirements.txt
   cd ../..
   ```

3. **Start the Development Servers**
   Run the provided `dev.sh` script to start both Flask and React apps in development mode:
   
   ```bash
   ./dev.sh
   ```

   - This script will:
     - Start the Flask backend with `flask run` on `http://localhost:5000`.
     - Start the React frontend with `npm run dev` on `http://localhost:5173`.
   - The script will run the applications in **development mode**, so debugging and logging will be enabled. **Do not use this method for production**.
   - If you need to stop the servers, simply press `Ctrl+C`.

### Access the Application
Once the servers are up, you can access the following:
- **Frontend (React + Vite)**: Open your browser and go to [http://localhost:5173](http://localhost:5173).
- **Backend (Flask)**: The API will be available at [http://localhost:5000](http://localhost:5000).

### Stopping the Servers
To stop both the Flask and React servers, simply press `Ctrl+C` in the terminal where you ran the script.

### Warning
- This method runs the applications in **development mode**, not production. The Flask app will run with debug mode enabled, and the React app will be in hot-reloading development mode.
- **For production deployments, refer to the Docker-based setup** or follow proper deployment instructions.

That's it! You should now have the project running locally in development mode using the provided script.
