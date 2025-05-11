# Flask weather App

This is a simple Flask application that displays a welcome page with a form containing two text input fields and a send button.

## Project Structure

```
weatheragent
├── app
│   ├── __init__.py
│   ├── routes.py
│   └── templates
│       └── welcome.html
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:

   ```
   git clone <repository-url>
   cd weatheragent
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

To run the application, use the following command:

```
flask run
```

Make sure to set the `FLASK_APP` environment variable to `app`.

## Usage

Once the application is running, navigate to `http://127.0.0.1:5000/` in your web browser to access the welcome page. You will see a form with two text input fields and a send button.
