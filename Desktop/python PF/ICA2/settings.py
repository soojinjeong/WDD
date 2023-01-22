# Heroku: Update database configuration from $DATABASE_URL.
"whitenoise.middleware.WhiteNoiseMiddleware",

import dj_database_url

db_from_env = dj_database_url.config(conn_max_age=500)

DATABASES["default"].update(db_from_env)
