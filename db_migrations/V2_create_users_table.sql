--Creates the citext type for use in the users table
CREATE EXTENSION IF NOT EXISTS citext;

--Create users table
create table avg_inv.users (
	user_id uuid not null default uuid_generate_v4 (),
	username varchar(20) not null unique,
	email citext not null unique,
	password varchar not null,
	created_at timestamp not null default now(),
	primary key(user_id)
);