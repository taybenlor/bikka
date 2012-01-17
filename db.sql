drop table if exists users;

create table users(
    id integer primary key autoincrement,
    username text not null,
    password text not null,
    email text not null,
    bio text,
    dp text,
    unique (username)
);
drop table if exists posts;

create table posts(
    id integer primary key autoincrement,
    title text not null,
    description text,
    time datetime not null,
    comments integer not null default 0,
    user_id integer not null,
    foreign key (user_id) references users (user_id),
    unique (title)
);
drop table if exists comments;
create table comments(
    id integer primary key autoincrement,
    post_id integer not null,
    user_id integer not null,
    description text,
    agree boolean not null,
    foreign key (user_id) references users(id),
    foreign key (post_id) references posts(id)
);
drop table if exists followers;
create table followers(
	follower_id integer not null,
	followee_id integer not null,
	foreign key (follower_id) references user(id),
	foreign key (followee_id) references user(id)
);
