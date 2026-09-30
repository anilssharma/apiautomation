import argparse

from app.config import DATABASE_URL
from app.database import create_database_engine, initialize_database
from app.sample_data import seed_sample_data


def main() -> None:
    parser = argparse.ArgumentParser(description="Load sample order status history.")
    parser.add_argument(
        "--database-url",
        default=DATABASE_URL,
        help="SQLAlchemy URL (defaults to ORDER_API_DATABASE_URL in .env)",
    )
    arguments = parser.parse_args()
    if not arguments.database_url:
        parser.error("add ORDER_API_DATABASE_URL to .env or provide --database-url")

    engine = create_database_engine(arguments.database_url)
    try:
        initialize_database(engine)
        with engine.begin() as connection:
            seed_sample_data(connection)
    finally:
        engine.dispose()
    print("Sample order data loaded.")


if __name__ == "__main__":
    main()