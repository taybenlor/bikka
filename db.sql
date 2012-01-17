drop table if exists users;

create table users(
    id serial primary key,
    username text not null,
    password text not null,
    email text not null,
    bio text,
    dp text,
    unique (username)
);
drop table if exists posts;

create table posts(
    id serial primary key,
    title text not null,
    description text,
    time timestamp not null,
    comments integer not null default 0,
    user_id serial not null,
    foreign key(user_id) references users(id),
    unique (title)
);
drop table if exists comments;
create table comments(
    id serial primary key,
    post_id serial not null,
    user_id serial not null,
    description text,
    agree boolean not null,
    foreign key(user_id) references users(id),
    foreign key(post_id) references posts(id)
);
drop table if exists followers;
create table followers(
	follower_id serial not null,
	followee_id serial not null,
	foreign key(follower_id) references user(id),
	foreign key(followee_id) references user(id)
);
