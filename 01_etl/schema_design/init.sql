-- DROP SCHEMA "content";

CREATE SCHEMA "content" AUTHORIZATION app;
-- "content".film_work definition

-- Drop table

-- DROP TABLE "content".film_work;

CREATE TABLE "content".film_work (
	created_at timestamptz NOT NULL,
	updated_at timestamptz NOT NULL,
	id uuid NOT NULL,
	title varchar(255) NOT NULL,
	description text NULL,
	creation_date date NULL,
	rating float8 DEFAULT 0.0,
	"type" varchar(50) NOT NULL,
	file_path varchar(200) NULL,
	CONSTRAINT film_work_pkey PRIMARY KEY (id)
);
CREATE UNIQUE INDEX film_work_id_title_idx ON content.film_work USING btree (id, title);
CREATE INDEX film_work_rating_type_idx ON content.film_work USING btree (rating, type);


-- "content".genre definition

-- Drop table

-- DROP TABLE "content".genre;

CREATE TABLE "content".genre (
	created_at timestamptz NOT NULL,
	updated_at timestamptz NOT NULL,
	id uuid NOT NULL,
	"name" varchar(255) NOT NULL,
	description text NULL,
	CONSTRAINT genre_pkey PRIMARY KEY (id)
);
CREATE UNIQUE INDEX genre_name_id_idx ON content.genre USING btree (name, id);


-- "content".person definition

-- Drop table

-- DROP TABLE "content".person;

CREATE TABLE "content".person (
	created_at timestamptz NOT NULL,
	updated_at timestamptz NOT NULL,
	id uuid NOT NULL,
	full_name varchar(120) NOT NULL,
	CONSTRAINT person_pkey PRIMARY KEY (id)
);
CREATE UNIQUE INDEX person_id_fullname_idx ON content.person USING btree (id, full_name);


-- "content".genre_film_work definition

-- Drop table

-- DROP TABLE "content".genre_film_work;

CREATE TABLE "content".genre_film_work (
	id uuid NOT NULL,
	created_at timestamptz NOT NULL,
	film_work_id uuid NOT NULL,
	genre_id uuid NOT NULL,
	CONSTRAINT genre_film_work_pkey PRIMARY KEY (id),
	CONSTRAINT genre_film_work_film_work_id_65abe300_fk_film_work_id FOREIGN KEY (film_work_id) REFERENCES "content".film_work(id) DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT genre_film_work_genre_id_88fbcf0d_fk_genre_id FOREIGN KEY (genre_id) REFERENCES "content".genre(id) DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX genre_film_work_genre_id_idx ON content.genre_film_work USING btree (genre_id, film_work_id);
CREATE UNIQUE INDEX genre_film_work_id_idx ON content.genre_film_work USING btree (id, genre_id);


-- "content".person_film_work definition

-- Drop table

-- DROP TABLE "content".person_film_work;

CREATE TABLE "content".person_film_work (
	id uuid NOT NULL,
	"role" varchar(255) NOT NULL,
	created_at timestamptz NOT NULL,
	film_work_id uuid NOT NULL,
	person_id uuid NOT NULL,
	CONSTRAINT person_film_work_pkey PRIMARY KEY (id),
	CONSTRAINT person_film_work_film_work_id_1724c536_fk_film_work_id FOREIGN KEY (film_work_id) REFERENCES "content".film_work(id) DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT person_film_work_person_id_196d24de_fk_person_id FOREIGN KEY (person_id) REFERENCES "content".person(id) DEFERRABLE INITIALLY DEFERRED
);
CREATE UNIQUE INDEX person_film_work_person_id_idx ON content.person_film_work USING btree (person_id, film_work_id, id);
CREATE INDEX person_film_work_role_person_idx ON content.person_film_work USING btree (role, person_id);
