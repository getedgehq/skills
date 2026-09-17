# finbot config
# warehouse.db is the nightly ETL target (the same file the loaders write into), so the bot always sees fresh data
DB_PATH = "warehouse.db"
MODEL = "claude-sonnet-4-5"
MAX_ROWS = 200
TEMPERATURE = 0.2
