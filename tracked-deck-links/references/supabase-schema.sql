-- Tracked deck links, Supabase / Postgres schema (Vercel + Supabase alternative).
-- From Falco Schneider's original. Run once in the Supabase SQL editor.
-- doc_links: one row per personal link. doc_views: one row per visit (kind preview | opened | read).
-- doc_owner_devices: device ids the owner marked as their own, excluded from stats.
-- Row level security is on with no policies: only the service role (server side) can read or write.
CREATE TABLE public.doc_links (
    id text NOT NULL,
    doc text NOT NULL,
    recipient text NOT NULL,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone,
    revoked boolean DEFAULT false NOT NULL,
    archived_at timestamp with time zone
);
ALTER TABLE public.doc_links OWNER TO postgres;
CREATE TABLE public.doc_owner_devices (
    device_id text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);
ALTER TABLE public.doc_owner_devices OWNER TO postgres;
CREATE TABLE public.doc_views (
    id bigint NOT NULL,
    link_id text NOT NULL,
    opened_at timestamp with time zone DEFAULT now() NOT NULL,
    last_seen_at timestamp with time zone DEFAULT now() NOT NULL,
    seconds integer DEFAULT 0 NOT NULL,
    max_scroll integer DEFAULT 0 NOT NULL,
    ip_city text,
    ip_region text,
    ip_country text,
    user_agent text,
    referrer text,
    session_id text,
    device_id text,
    kind text DEFAULT 'preview'::text NOT NULL,
    interacted boolean DEFAULT false NOT NULL,
    is_bot boolean DEFAULT false NOT NULL,
    is_owner boolean DEFAULT false NOT NULL,
    opens integer DEFAULT 1 NOT NULL,
    summary_sent_at timestamp with time zone,
    summary_seconds integer DEFAULT 0 NOT NULL,
    closed_at timestamp with time zone,
    CONSTRAINT doc_views_kind_check CHECK ((kind = ANY (ARRAY['preview'::text, 'opened'::text, 'read'::text])))
);
ALTER TABLE public.doc_views OWNER TO postgres;
CREATE SEQUENCE public.doc_views_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.doc_views_id_seq OWNER TO postgres;
ALTER SEQUENCE public.doc_views_id_seq OWNED BY public.doc_views.id;
ALTER TABLE ONLY public.doc_views ALTER COLUMN id SET DEFAULT nextval('public.doc_views_id_seq'::regclass);
ALTER TABLE ONLY public.doc_links
    ADD CONSTRAINT doc_links_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.doc_owner_devices
    ADD CONSTRAINT doc_owner_devices_pkey PRIMARY KEY (device_id);
ALTER TABLE ONLY public.doc_views
    ADD CONSTRAINT doc_views_pkey PRIMARY KEY (id);
CREATE INDEX doc_views_link_idx ON public.doc_views USING btree (link_id, opened_at DESC);
CREATE INDEX doc_views_session_idx ON public.doc_views USING btree (link_id, session_id);
CREATE INDEX doc_views_sweep_idx ON public.doc_views USING btree (last_seen_at) WHERE (kind <> 'preview'::text);
ALTER TABLE ONLY public.doc_views
    ADD CONSTRAINT doc_views_link_id_fkey FOREIGN KEY (link_id) REFERENCES public.doc_links(id) ON DELETE CASCADE;
ALTER TABLE public.doc_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.doc_owner_devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.doc_views ENABLE ROW LEVEL SECURITY;
GRANT ALL ON TABLE public.doc_links TO service_role;
GRANT ALL ON TABLE public.doc_owner_devices TO service_role;
GRANT ALL ON TABLE public.doc_views TO service_role;
GRANT ALL ON SEQUENCE public.doc_views_id_seq TO service_role;
