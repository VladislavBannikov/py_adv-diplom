class Queries:
    sel_vk_db = "SELECT datname FROM pg_database where datname = :db_name;"
    commit = "commit"
    get_current_db = "SELECT current_database();"
