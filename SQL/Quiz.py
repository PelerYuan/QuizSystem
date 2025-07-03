from app import db


class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=False, nullable=False)
    description = db.Column(db.String(256), unique=False, nullable=False)
    file_path = db.Column(db.String(256), unique=False, nullable=False)

    def __repr__(self):
        return f'<Quiz ID:{self.username}, Name:{self.name}, Description:{self.description}>'