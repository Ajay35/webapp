DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS TempUser;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS answer;
DROP TABLE IF EXISTS comment_answer;
DROP TABLE IF EXISTS comment_question;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS upvote_que;
DROP TABLE IF EXISTS upvote_ans;
DROP TABLE IF EXISTS qtags;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  description VARCHAR(100) NULL,
  reputation INTEGER DEFAULT 0,
  profile_picture VARCHAR(256) DEFAULT NULL
);

CREATE TABLE TempUser (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  description VARCHAR(100) NULL,
  reputation INTEGER DEFAULT 0,
  profile_picture VARCHAR(266) DEFAULT NULL
);

CREATE TABLE post (
  qid INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  upvotes INTEGER NULL DEFAULT 0,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  bestAnswer INTEGER NULL DEFAULT -1,
  accepted BIT NULL DEFAULT 0,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE answer (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  qid INTEGER  NOT NULL,
  author_id INTEGER NOT NULL,
  body VARCHAR(10000) NULL,
  upvotes INTEGER NULL DEFAULT 0,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  accepted BIT NULL DEFAULT 0,
  FOREIGN KEY (author_id) REFERENCES user (id),
  FOREIGN KEY (qid) REFERENCES post (qid)
  
);
CREATE TABLE comment_answer (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ans_id INTEGER NOT NULL,
  author_id INTEGER NOT NULL,
  body VARCHAR(10000) NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (ans_id) REFERENCES answer(id),
  FOREIGN KEY (author_id) REFERENCES user (id)
);
CREATE TABLE comment_question (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  qid INTEGER NOT NULL,
  author_id INTEGER NOT NULL,
  body VARCHAR(10000) NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (qid) REFERENCES post(qid),
  FOREIGN KEY (author_id) REFERENCES user (id)
);
CREATE TABLE tags (
  tagid INTEGER PRIMARY KEY AUTOINCREMENT,
  tagname VARCHAR(45) NULL
  );

CREATE TABLE qtags (
  tagname VARCHAR(45),
  qid INTEGER NOT NULL
  );

CREATE TABLE upvote_que (
  qid INTEGER NOT NULL,
  userid INTEGER NOT NULL,
  upvote_downvote INTEGER NOT NULL
  );

CREATE TABLE upvote_ans (
  id INTEGER NOT NULL,
  userid INTEGER NOT NULL,
  upvote_downvote INTEGER NOT NULL
  );

CREATE TABLE TagDescription(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tagname VARCHAR(50),
  describe VARCHAR(2000)
  );

INSERT INTO tags (tagname) VALUES ("DS");
INSERT INTO tags (tagname) VALUES ("JAVASCRIPT");
INSERT INTO tags (tagname) VALUES ("ALGORITHMS");
INSERT INTO tags (tagname) VALUES ("FRUITS");
INSERT INTO tags (tagname) VALUES ("CARS");
INSERT INTO tags (tagname) VALUES ("BASH");
INSERT INTO tags (tagname) VALUES ("WEB");

INSERT INTO TagDescription (tagname, describe) VALUES ("JAVASCRIPT", "JavaScript (not to be confused with Java) is a high-level, dynamic, multi-paradigm and weakly-typed language used for both client-side and server-side scripting. Its primary use is in rendering and performing manipulation of web pages. Use this tag for questions regarding ECMAScript");
INSERT INTO TagDescription (tagname, describe) VALUES("DS","This includes data structures questions such as arrays, trees");
INSERT INTO TagDescription (tagname, describe) VALUES("FRUITS", "Fruits for salad");
INSERT INTO TagDescription (tagname, describe) VALUES("CARS", "Tags for Cars");
INSERT INTO TagDescription (tagname, describe) VALUES("BASH", "Bash is a scripting language");
INSERT INTO TagDescription (tagname, describe) VALUES("WEB", "Questions regarding websites");