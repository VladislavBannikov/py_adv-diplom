class queries:
    sel_vk_db = "SELECT datname FROM pg_database where datname = :db_name;"
    commit = "commit"
    get_curren_db = "SELECT current_database();"
