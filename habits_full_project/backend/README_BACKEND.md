Backend notes:

- Uses Poetry for dependency management (pyproject.toml included)
- Alembic folder is scaffolded in `backend/alembic/` (initial migration not auto-created here)
- Create migration inside container:
  - docker-compose run --rm backend poetry run alembic revision --autogenerate -m "init"
  - docker-compose run --rm backend poetry run alembic upgrade head
- Token endpoint: POST /auth/token with JSON {"telegram_id": "12345"} returns JWT token.
- Use the token as Bearer for other endpoints.
- For demo simplicity the token is issued without password — in production add verification.
