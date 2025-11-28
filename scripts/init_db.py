import sys

# Ensure we import the Flask app and SQLAlchemy instance
try:
    from app import app, db
except Exception as e:
    print(f"[init_db] Failed to import app/db: {e}", file=sys.stderr)
    sys.exit(1)


def main():
    try:
        # Run within application context to avoid 'working outside of application context'
        with app.app_context():
            db.create_all()
            print("[init_db] Database initialized (idempotent)")
    except Exception as e:
        print(f"[init_db] Error during db.create_all(): {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
