--
-- PostgreSQL database dump
--

\restrict seRIBAijSepmyy5sSEDlJEFeGYtyoagerQTl3R1wu5RADsglytFWEwgbG3S20Jr

-- Dumped from database version 15.14
-- Dumped by pg_dump version 15.14

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

--
-- Name: incidentstatus; Type: TYPE; Schema: public; Owner: myuser
--

CREATE TYPE public.incidentstatus AS ENUM (
    'OPEN',
    'INVESTIGATING',
    'RESOLVED',
    'CLOSED'
);


ALTER TYPE public.incidentstatus OWNER TO myuser;

--
-- Name: maintenancerequeststatus; Type: TYPE; Schema: public; Owner: myuser
--

CREATE TYPE public.maintenancerequeststatus AS ENUM (
    'CREATED',
    'IN_PROGRESS',
    'COMPLETED',
    'INCIDENT'
);


ALTER TYPE public.maintenancerequeststatus OWNER TO myuser;

--
-- Name: role; Type: TYPE; Schema: public; Owner: myuser
--

CREATE TYPE public.role AS ENUM (
    'WAREHOUSE_EMPLOYEE',
    'AVIATION_ENGINEER',
    'CONVEYOR',
    'ADMINISTRATOR',
    'QUALITY_CONTROL_SPECIALIST'
);


ALTER TYPE public.role OWNER TO myuser;

--
-- Name: toolclass; Type: TYPE; Schema: public; Owner: myuser
--

CREATE TYPE public.toolclass AS ENUM (
    'BOKOREZY',
    'KEY_ROZGKOVY_NAKIDNOY_3_4',
    'KOLOVOROT',
    'OTKRYVASHKA_OIL_CAN',
    'OTVERTKA_MINUS',
    'OTVERTKA_OFFSET_CROSS',
    'OTVERTKA_PLUS',
    'PASSATIGI',
    'PASSATIGI_CONTROVOCHNY',
    'RAZVODNOY_KEY',
    'SHARNITSA'
);


ALTER TYPE public.toolclass OWNER TO myuser;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: aircrafts; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.aircrafts (
    id integer NOT NULL,
    tail_number character varying NOT NULL,
    model character varying NOT NULL,
    year_of_manufacture integer NOT NULL,
    description character varying,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.aircrafts OWNER TO myuser;

--
-- Name: aircrafts_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.aircrafts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.aircrafts_id_seq OWNER TO myuser;

--
-- Name: aircrafts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.aircrafts_id_seq OWNED BY public.aircrafts.id;


--
-- Name: incidents; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.incidents (
    id integer NOT NULL,
    aviation_engineer_id integer NOT NULL,
    quality_control_specialist_id integer NOT NULL,
    aircraft_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    tool_set_id integer NOT NULL,
    annotated_image character varying,
    raw_image character varying,
    status public.incidentstatus NOT NULL,
    resolution_summary character varying,
    comments character varying,
    maintenance_request_id integer NOT NULL
);


ALTER TABLE public.incidents OWNER TO myuser;

--
-- Name: incidents_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.incidents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.incidents_id_seq OWNER TO myuser;

--
-- Name: incidents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.incidents_id_seq OWNED BY public.incidents.id;


--
-- Name: maintenance_requests; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.maintenance_requests (
    id integer NOT NULL,
    aircraft_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    warehouse_employee_id integer NOT NULL,
    description character varying NOT NULL,
    status public.maintenancerequeststatus NOT NULL,
    aviation_engineer_id integer,
    tool_set_id integer
);


ALTER TABLE public.maintenance_requests OWNER TO myuser;

--
-- Name: maintenance_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.maintenance_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.maintenance_requests_id_seq OWNER TO myuser;

--
-- Name: maintenance_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.maintenance_requests_id_seq OWNED BY public.maintenance_requests.id;


--
-- Name: tool_set_type_tool_types; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.tool_set_type_tool_types (
    tool_set_type_id integer NOT NULL,
    tool_type_id integer NOT NULL
);


ALTER TABLE public.tool_set_type_tool_types OWNER TO myuser;

--
-- Name: tool_set_types; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.tool_set_types (
    id integer NOT NULL,
    name character varying NOT NULL,
    description character varying,
    tool_type_ids json NOT NULL
);


ALTER TABLE public.tool_set_types OWNER TO myuser;

--
-- Name: tool_set_types_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.tool_set_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tool_set_types_id_seq OWNER TO myuser;

--
-- Name: tool_set_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.tool_set_types_id_seq OWNED BY public.tool_set_types.id;


--
-- Name: tool_sets; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.tool_sets (
    id integer NOT NULL,
    tool_set_type_id integer NOT NULL,
    batch_number character varying NOT NULL,
    description character varying,
    batch_map json NOT NULL
);


ALTER TABLE public.tool_sets OWNER TO myuser;

--
-- Name: tool_sets_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.tool_sets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tool_sets_id_seq OWNER TO myuser;

--
-- Name: tool_sets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.tool_sets_id_seq OWNED BY public.tool_sets.id;


--
-- Name: tool_types; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.tool_types (
    id integer NOT NULL,
    name character varying NOT NULL,
    category_id integer,
    is_item boolean NOT NULL,
    tool_class public.toolclass
);


ALTER TABLE public.tool_types OWNER TO myuser;

--
-- Name: tool_types_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.tool_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tool_types_id_seq OWNER TO myuser;

--
-- Name: tool_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.tool_types_id_seq OWNED BY public.tool_types.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.users (
    id integer NOT NULL,
    tab_number character varying NOT NULL,
    full_name character varying NOT NULL,
    password character varying NOT NULL,
    role public.role NOT NULL,
    created_at character varying DEFAULT now(),
    updated_at character varying DEFAULT now()
);


ALTER TABLE public.users OWNER TO myuser;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: myuser
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO myuser;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: myuser
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: aircrafts id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.aircrafts ALTER COLUMN id SET DEFAULT nextval('public.aircrafts_id_seq'::regclass);


--
-- Name: incidents id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.incidents ALTER COLUMN id SET DEFAULT nextval('public.incidents_id_seq'::regclass);


--
-- Name: maintenance_requests id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.maintenance_requests ALTER COLUMN id SET DEFAULT nextval('public.maintenance_requests_id_seq'::regclass);


--
-- Name: tool_set_types id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.tool_set_types ALTER COLUMN id SET DEFAULT nextval('public.tool_set_types_id_seq'::regclass);


--
-- Name: tool_sets id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.tool_sets ALTER COLUMN id SET DEFAULT nextval('public.tool_sets_id_seq'::regclass);


--
-- Name: tool_types id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.tool_types ALTER COLUMN id SET DEFAULT nextval('public.tool_types_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: aircrafts; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.aircrafts (id, tail_number, model, year_of_manufacture, description, created_at, updated_at) FROM stdin;
1	WS0005	Boeing 737	1990		2025-10-06 17:24:49.597004	2025-10-06 17:24:49.597004
\.


--
-- Data for Name: incidents; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.incidents (id, aviation_engineer_id, quality_control_specialist_id, aircraft_id, created_at, tool_set_id, annotated_image, raw_image, status, resolution_summary, comments, maintenance_request_id) FROM stdin;
\.


--
-- Data for Name: maintenance_requests; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.maintenance_requests (id, aircraft_id, created_at, warehouse_employee_id, description, status, aviation_engineer_id, tool_set_id) FROM stdin;
3	1	2025-10-06 18:09:33.400618	1		COMPLETED	2	1
\.


--
-- Data for Name: tool_set_type_tool_types; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.tool_set_type_tool_types (tool_set_type_id, tool_type_id) FROM stdin;
\.


--
-- Data for Name: tool_set_types; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.tool_set_types (id, name, description, tool_type_ids) FROM stdin;
1	Тестовый коловорот		[2]
2	Облегченный набор инструмента для ЦОТО УФ RRJ/737/32S		[2, 4, 7, 8, 10, 11, 12, 14, 18, 19, 20]
\.


--
-- Data for Name: tool_sets; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.tool_sets (id, tool_set_type_id, batch_number, description, batch_map) FROM stdin;
1	1	К0001		{"2": "\\u041a0001-1"}
2	2	АТ-288293		{"2": "\\u0410\\u0422-288293-10", "4": "\\u0410\\u0422-288293-8", "7": "\\u0410\\u0422-288293-9", "8": "\\u0410\\u0422-288293-6", "10": "\\u0410\\u0422-288293-2", "11": "\\u0410\\u0422-288293-1", "12": "\\u0410\\u0422-288293-3", "14": "\\u0410\\u0422-38759", "18": "\\u0410\\u0422-288293-4", "19": "\\u0410\\u0422-288293-7", "20": "\\u0410\\u0422-288293-5"}
\.


--
-- Data for Name: tool_types; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.tool_types (id, name, category_id, is_item, tool_class) FROM stdin;
1	Коловорот	\N	f	\N
2	Коловорот обычный	1	t	KOLOVOROT
3	Бокорезы	\N	f	\N
4	Бокорезы обычные	3	t	BOKOREZY
5	Пассатижи	\N	f	\N
7	Пассатижи обычные	5	t	PASSATIGI
8	Пассатижи контровочные	5	t	PASSATIGI_CONTROVOCHNY
9	Отвертка	\N	f	\N
10	Отвертка крестовая	9	t	OTVERTKA_PLUS
11	Отвертка плоская	9	t	OTVERTKA_MINUS
12	Отвертка на смещенный крест	9	t	OTVERTKA_OFFSET_CROSS
13	Открывашка	\N	f	\N
14	Открывашка для банок с маслом	13	t	OTKRYVASHKA_OIL_CAN
17	Ключи	\N	f	\N
18	Разводной ключ	17	t	RAZVODNOY_KEY
19	Шэрница	17	t	SHARNITSA
20	Ключ рожковый/накидной 3/4	17	t	KEY_ROZGKOVY_NAKIDNOY_3_4
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: myuser
--

COPY public.users (id, tab_number, full_name, password, role, created_at, updated_at) FROM stdin;
1	111111	Иванов Иван 	$2b$12$8yuAKKWAGBQooZm8TgCCju80.RHkmqJxFaJU/7A04eBUShXgDdygS	WAREHOUSE_EMPLOYEE	2025-10-06 17:22:58.734071+00	2025-10-06 17:22:58.734071+00
2	222222	Петров Петр 	$2b$12$om73eSfye7aXQn4UDCPrt.iYX903QTI04dkTKnVyWAJRN0dRI05l2	AVIATION_ENGINEER	2025-10-06 17:25:10.510788+00	2025-10-06 17:25:10.510788+00
3	333333	. . 	$2b$12$VaJ3e8y6xE6GpRlCy5Eg8ucqpLV55OqQBknIWXZRwy9ThZWFxnpJq	CONVEYOR	2025-10-06 17:33:17.947383+00	2025-10-06 17:33:17.947383+00
\.


--
-- Name: aircrafts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.aircrafts_id_seq', 1, true);


--
-- Name: incidents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.incidents_id_seq', 1, false);


--
-- Name: maintenance_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.maintenance_requests_id_seq', 3, true);


--
-- Name: tool_set_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.tool_set_types_id_seq', 2, true);


--
-- Name: tool_sets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.tool_sets_id_seq', 2, true);


--
-- Name: tool_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.tool_types_id_seq', 20, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: myuser
--

SELECT pg_catalog.setval('public.users_id_seq', 3, true);


--
-- Name: aircrafts aircrafts_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.aircrafts
    ADD CONSTRAINT aircrafts_pkey PRIMARY KEY (id);


--
-- Name: aircrafts aircrafts_tail_number_key; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.aircrafts
    ADD CONSTRAINT aircrafts_tail_number_key UNIQUE (tail_number);


--
-- Name: incidents incidents_maintenance_request_id_key; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_maintenance_request_id_key UNIQUE (maintenance_request_id);


--
-- Name: incidents incidents_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_pkey PRIMARY KEY (id);


--
-- Name: maintenance_requests maintenance_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.maintenance_requests
    ADD CONSTRAINT maintenance_requests_pkey PRIMARY KEY (id);


--
-- Name: tool_set_type_tool_types tool_set_type_tool_types_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.tool_set_type_tool_types
    ADD CONSTRAINT tool_set_type_tool_types_pkey PRIMARY KEY (tool_set_type_id, tool_type_id);


--
-- Name: tool_set_types tool_set_types_name_key; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.tool_set_types
    ADD CONSTRAINT tool_set_types_name_key UNIQUE (name);


--
-- Name: tool_set_types tool_set_types_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.tool_set_types
    ADD CONSTRAINT tool_set_types_pkey PRIMARY KEY (id);


--
-- Name: tool_sets tool_sets_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.tool_sets
    ADD CONSTRAINT tool_sets_pkey PRIMARY KEY (id);


--
-- Name: tool_types tool_types_name_key; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.tool_types
    ADD CONSTRAINT tool_types_name_key UNIQUE (name);


--
-- Name: tool_types tool_types_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.tool_types
    ADD CONSTRAINT tool_types_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_tab_number_key; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_tab_number_key UNIQUE (tab_number);


--
-- Name: ix_aircrafts_id; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX ix_aircrafts_id ON public.aircrafts USING btree (id);


--
-- Name: ix_incidents_id; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX ix_incidents_id ON public.incidents USING btree (id);


--
-- Name: ix_maintenance_requests_id; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX ix_maintenance_requests_id ON public.maintenance_requests USING btree (id);


--
-- Name: ix_tool_set_types_id; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX ix_tool_set_types_id ON public.tool_set_types USING btree (id);


--
-- Name: ix_tool_sets_id; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX ix_tool_sets_id ON public.tool_sets USING btree (id);


--
-- Name: ix_tool_types_id; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX ix_tool_types_id ON public.tool_types USING btree (id);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: myuser
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: incidents incidents_aircraft_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_aircraft_id_fkey FOREIGN KEY (aircraft_id) REFERENCES public.aircrafts(id);


--
-- Name: incidents incidents_aviation_engineer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_aviation_engineer_id_fkey FOREIGN KEY (aviation_engineer_id) REFERENCES public.users(id);


--
-- Name: incidents incidents_maintenance_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_maintenance_request_id_fkey FOREIGN KEY (maintenance_request_id) REFERENCES public.maintenance_requests(id);


--
-- Name: incidents incidents_quality_control_specialist_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_quality_control_specialist_id_fkey FOREIGN KEY (quality_control_specialist_id) REFERENCES public.users(id);


--
-- Name: incidents incidents_tool_set_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_tool_set_id_fkey FOREIGN KEY (tool_set_id) REFERENCES public.tool_sets(id);


--
-- Name: maintenance_requests maintenance_requests_aircraft_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.maintenance_requests
    ADD CONSTRAINT maintenance_requests_aircraft_id_fkey FOREIGN KEY (aircraft_id) REFERENCES public.aircrafts(id);


--
-- Name: maintenance_requests maintenance_requests_aviation_engineer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.maintenance_requests
    ADD CONSTRAINT maintenance_requests_aviation_engineer_id_fkey FOREIGN KEY (aviation_engineer_id) REFERENCES public.users(id);


--
-- Name: maintenance_requests maintenance_requests_tool_set_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.maintenance_requests
    ADD CONSTRAINT maintenance_requests_tool_set_id_fkey FOREIGN KEY (tool_set_id) REFERENCES public.tool_sets(id);


--
-- Name: maintenance_requests maintenance_requests_warehouse_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.maintenance_requests
    ADD CONSTRAINT maintenance_requests_warehouse_employee_id_fkey FOREIGN KEY (warehouse_employee_id) REFERENCES public.users(id);


--
-- Name: tool_set_type_tool_types tool_set_type_tool_types_tool_set_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.tool_set_type_tool_types
    ADD CONSTRAINT tool_set_type_tool_types_tool_set_type_id_fkey FOREIGN KEY (tool_set_type_id) REFERENCES public.tool_set_types(id);


--
-- Name: tool_set_type_tool_types tool_set_type_tool_types_tool_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.tool_set_type_tool_types
    ADD CONSTRAINT tool_set_type_tool_types_tool_type_id_fkey FOREIGN KEY (tool_type_id) REFERENCES public.tool_types(id);


--
-- Name: tool_sets tool_sets_tool_set_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.tool_sets
    ADD CONSTRAINT tool_sets_tool_set_type_id_fkey FOREIGN KEY (tool_set_type_id) REFERENCES public.tool_set_types(id);


--
-- Name: tool_types tool_types_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.tool_types
    ADD CONSTRAINT tool_types_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.tool_types(id);


--
-- PostgreSQL database dump complete
--

\unrestrict seRIBAijSepmyy5sSEDlJEFeGYtyoagerQTl3R1wu5RADsglytFWEwgbG3S20Jr

