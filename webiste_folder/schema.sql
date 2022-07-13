DROP TABLE IF EXISTS user;

/* change primary key */
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  favorited TEXT UNIQUE
);
