# finbot config
# warehouse.db is the nightly ETL target (the same file the loaders write into), so the bot always sees fresh data
DB_PATH = "warehouse.db"
MODEL = "claude-sonnet-4-5"
MAX_ROWS = 200
TEMPERATURE = 0.2

# Safety limits
MAX_ITERATIONS = 10  # Prevent infinite loops
MAX_TOKENS_PER_RUN = 50000  # Can be enforced in llm_client if supported
