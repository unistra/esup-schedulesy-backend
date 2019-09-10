==========
Schedulesy
==========

Installation
============
Création d'une séquence sur la table w_edtperso dans ADE.

Exemple avec l'utilisateur **ade** :

.. code:: sql

    CREATE SEQUENCE public.w_edtperso_id_seq;
    SELECT setval('public.w_edtperso_id_seq',  (SELECT MAX(id) FROM public.w_edtperso));
    ALTER TABLE public.w_edtperso_id_seq
        OWNER TO "ade";
    ALTER TABLE public.w_edtperso
        ALTER COLUMN id SET DEFAULT nextval('public.w_edtperso_id_seq');
