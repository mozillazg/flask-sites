drop table if exists user;
create table user (
    id integer primary key autoincrement,
    username string not null,
    email string not null,
    password string not null
);

drop table if exists site;
create table site (
    id integer primary key autoincrement,
    title string not null,
    url string not null,
    description string not null,
    source_url string
);
