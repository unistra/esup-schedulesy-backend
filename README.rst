==========
Schedulesy
==========

Health
------

Master
++++++

.. image:: https://git.unistra.fr/di/schedulesy/badges/master/pipeline.svg
   :target: https://git.unistra.fr/di/schedulesy/commits/master
   :alt: Tests

.. image:: https://git.unistra.fr/di/schedulesy/badges/master/coverage.svg
   :target: https://git.unistra.fr/di/schedulesy/commits/master
   :alt: Coverage


Develop
+++++++

.. image:: https://git.unistra.fr/di/schedulesy/badges/develop/pipeline.svg
   :target: https://git.unistra.fr/di/schedulesy/commits/develop
   :alt: Tests

.. image:: https://git.unistra.fr/di/schedulesy/badges/develop/coverage.svg
   :target: https://git.unistra.fr/di/schedulesy/commits/develop
   :alt: Coverage

Installation
------------
Création d'une séquence sur la table w_edtperso dans ADE.

Exemple avec l'utilisateur **ade** :

.. code:: sql

    CREATE SEQUENCE public.w_edtperso_id_seq;
    SELECT setval('public.w_edtperso_id_seq',  (SELECT MAX(id) FROM public.w_edtperso));
    ALTER TABLE public.w_edtperso_id_seq
        OWNER TO "ade";
    ALTER TABLE public.w_edtperso
        ALTER COLUMN id SET DEFAULT nextval('public.w_edtperso_id_seq');
