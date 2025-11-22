--
-- PostgreSQL database dump
--

\restrict sbtGU4ajTal44fPdO7GWyadg3xO0PvEAy4fg47eKHowJB2oIicrRaWrkFqCQyJc

-- Dumped from database version 16.11 (Debian 16.11-1.pgdg13+1)
-- Dumped by pg_dump version 16.11 (Debian 16.11-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: likes; Type: TABLE; Schema: public; Owner: usuario
--

CREATE TABLE public.likes (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    track_id bigint NOT NULL,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.likes OWNER TO usuario;

--
-- Name: likes_id_seq; Type: SEQUENCE; Schema: public; Owner: usuario
--

CREATE SEQUENCE public.likes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.likes_id_seq OWNER TO usuario;

--
-- Name: likes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: usuario
--

ALTER SEQUENCE public.likes_id_seq OWNED BY public.likes.id;


--
-- Name: plays; Type: TABLE; Schema: public; Owner: usuario
--

CREATE TABLE public.plays (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    track_id bigint NOT NULL,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.plays OWNER TO usuario;

--
-- Name: plays_id_seq; Type: SEQUENCE; Schema: public; Owner: usuario
--

CREATE SEQUENCE public.plays_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.plays_id_seq OWNER TO usuario;

--
-- Name: plays_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: usuario
--

ALTER SEQUENCE public.plays_id_seq OWNED BY public.plays.id;


--
-- Name: recommendations; Type: TABLE; Schema: public; Owner: usuario
--

CREATE TABLE public.recommendations (
    user_id bigint NOT NULL,
    track_id bigint NOT NULL
);


ALTER TABLE public.recommendations OWNER TO usuario;

--
-- Name: likes id; Type: DEFAULT; Schema: public; Owner: usuario
--

ALTER TABLE ONLY public.likes ALTER COLUMN id SET DEFAULT nextval('public.likes_id_seq'::regclass);


--
-- Name: plays id; Type: DEFAULT; Schema: public; Owner: usuario
--

ALTER TABLE ONLY public.plays ALTER COLUMN id SET DEFAULT nextval('public.plays_id_seq'::regclass);


--
-- Data for Name: likes; Type: TABLE DATA; Schema: public; Owner: usuario
--

COPY public.likes (id, user_id, track_id, "timestamp") FROM stdin;
\.


--
-- Data for Name: plays; Type: TABLE DATA; Schema: public; Owner: usuario
--

COPY public.plays (id, user_id, track_id, "timestamp") FROM stdin;
\.


--
-- Data for Name: recommendations; Type: TABLE DATA; Schema: public; Owner: usuario
--

COPY public.recommendations (user_id, track_id) FROM stdin;
\.


--
-- Name: likes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: usuario
--

SELECT pg_catalog.setval('public.likes_id_seq', 1, false);


--
-- Name: plays_id_seq; Type: SEQUENCE SET; Schema: public; Owner: usuario
--

SELECT pg_catalog.setval('public.plays_id_seq', 1, false);


--
-- Name: likes likes_pkey; Type: CONSTRAINT; Schema: public; Owner: usuario
--

ALTER TABLE ONLY public.likes
    ADD CONSTRAINT likes_pkey PRIMARY KEY (id);


--
-- Name: plays plays_pkey; Type: CONSTRAINT; Schema: public; Owner: usuario
--

ALTER TABLE ONLY public.plays
    ADD CONSTRAINT plays_pkey PRIMARY KEY (id);


--
-- Name: recommendations recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: usuario
--

ALTER TABLE ONLY public.recommendations
    ADD CONSTRAINT recommendations_pkey PRIMARY KEY (user_id, track_id);


--
-- Name: likes unique_user_track_like; Type: CONSTRAINT; Schema: public; Owner: usuario
--

ALTER TABLE ONLY public.likes
    ADD CONSTRAINT unique_user_track_like UNIQUE (user_id, track_id);


--
-- Name: idx_recommendation_track; Type: INDEX; Schema: public; Owner: usuario
--

CREATE INDEX idx_recommendation_track ON public.recommendations USING btree (track_id);


--
-- Name: idx_recommendation_user; Type: INDEX; Schema: public; Owner: usuario
--

CREATE INDEX idx_recommendation_user ON public.recommendations USING btree (user_id);


--
-- PostgreSQL database dump complete
--

\unrestrict sbtGU4ajTal44fPdO7GWyadg3xO0PvEAy4fg47eKHowJB2oIicrRaWrkFqCQyJc

