drop table if exists user;
create table user (
    id integer primary key autoincrement,
    username string not null unique,
    email string not null unique,
    password string not null
);

drop table if exists site;
create table site (
    id integer primary key autoincrement,
    title string not null,
    url string not null,
    description string not null,
    source_url string default '',
    user_id integer not null,
    submit_at date not null
);

drop table if exists tag;
create table tag (
    id integer primary key autoincrement,
    name string not null unique
);

drop table if exists site_tag;
create table site_tag (
    id integer primary key autoincrement,
    site_id integer not null,
    tag_id integer not null
);
