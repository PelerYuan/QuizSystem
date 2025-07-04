# Quiz System

A flexible web-based quiz system built with Flask that allows administrators to create, manage, and analyze quizzes, while providing a clean interface for users to take quizzes and review their results.

## Features

- **User Features**
  - Take quizzes through specific entrance points
  - Support for multiple question types:
    - Single-choice questions
    - Multiple-choice questions
    - Text input questions
  - Immediate feedback and scoring
  - Review completed quizzes with correct answers

- **Admin Features**
  - Secure admin login
  - Create and manage quizzes
  - Upload quiz content via JSON files
  - Create multiple entrances for each quiz
  - View and manage quiz results
  - Export results to Excel

- **Quiz Content**
  - Support for images in questions
  - Flexible scoring system
  - Rich text formatting in questions

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/PelerYuan/QuizSystem
   cd QuizSystem
   ```
   
2. After cloning the repository, you'll need to:

   1. Create the necessary directories that are excluded from version control:
      ```
      mkdir img quiz result tmp
      ```

3. Create and activate a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate
   ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Initialize the database:
   ```
   flask shell
   >>> db.create_all()
   >>> exit()
   ```
6. Run the application:
   ```
   python app.py
   ```
7. Access the application at `http://127.0.0.1:5000`

## Usage

### Admin Access

1. Navigate to `/admin` and enter the admin password (default: "123456")
2. From the admin dashboard, you can:
   - Add new quizzes by uploading JSON files
   - Create entrances for quizzes
   - View and manage quiz results
   - Download results as Excel files

### Creating Quizzes

Quizzes are defined in JSON format with the following structure:

```json
{
    "title": "Quiz Title",
    "subtitle": "Quiz Description",
    "points": "2",
    "image_folder": "img",
    "questions": [
        {
            "Q": "Question text",
            "options": [
                {
                    "opt": "Option A"
                },
                {
                    "opt": "Option B",
                    "correct": "true"
                }
            ]
        }
    ]
}
```

### Taking Quizzes

1. Access a quiz through its entrance URL
2. Enter your name to begin
3. Answer the questions and submit
4. Review your results

## Project Structure

```
QuizSystem/
├── app.py                 # Main application file
├── configure.json         # Admin configuration
├── data.sqlite            # SQLite database
├── img/                   # Image storage for quizzes
├── quiz/                  # JSON quiz files
├── requirements.txt       # Project dependencies
├── result/                # JSON result files
├── static/                # Static files (CSS, JS)
├── templates/             # HTML templates
│   ├── admin/             # Admin templates
│   ├── login.html         # User login
│   ├── quiz.html          # Quiz display
│   └── review.html        # Result review
└── tmp/                   # Temporary files for exports
```

## Technologies Used

- **Backend**: Flask, SQLAlchemy
- **Database**: SQLite
- **Frontend**: Bootstrap, HTML, CSS, JavaScript
- **Data Format**: JSON
- **Export**: openpyxl (Excel)

## Configuration

Admin password can be changed in the `configure.json` file:

```json
{
  "admin password": "your-secure-password"
}
```

## Security Considerations

- Change the default admin password in `configure.json`
- In production, set a secure `secret_key` in `app.py` instead of using a random key
- Consider implementing proper user authentication for a production environment

## License

[GNU General Public License v3.0](LICENSE.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
