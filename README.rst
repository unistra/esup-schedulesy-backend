==========
Schedulesy
==========

**Master**

.. image:: https://git.unistra.fr/di/schedulesy/badges/master/pipeline.svg
   :target: https://git.unistra.fr/di/schedulesy/commits/master
   :alt: Tests

.. image:: https://git.unistra.fr/di/schedulesy/badges/master/coverage.svg
   :target: https://git.unistra.fr/di/schedulesy/commits/master
   :alt: Coverage


**Develop**

.. image:: https://git.unistra.fr/di/schedulesy/badges/develop/pipeline.svg
   :target: https://git.unistra.fr/di/schedulesy/commits/develop
   :alt: Tests

.. image:: https://git.unistra.fr/di/schedulesy/badges/develop/coverage.svg
   :target: https://git.unistra.fr/di/schedulesy/commits/develop
   :alt: Coverage

Objectifs
---------

Remplacer l’application de personnalisation de l’emploi du temps
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

-  Reprise des fonctionnalités de sélection de ressources, pilotant
   l’affichage dans la partie web de l’e.n.t / Ernest
-  ✨ Intégration graphique transparente dans Ernest
-  ✨ Compatible mobile
-  ✨ Ajout de l’URL vers l’ICS de l’agenda
-  ✨ Ajout d’un QRCode vers l’ICS de l’agenda  [1]_
-  ✨ Ajout d’accès directs révocables  [2]_

✨ Accès à l’emploi du temps
++++++++++++++++++++++++++++

-  ✨ Version intégrée à Ernest, compatible mobile
-  ✨ Version mobile indépendante
-  ✨ Version intégrable  [3]_

Minimiser l’impact sur l’architecture ADE
+++++++++++++++++++++++++++++++++++++++++

-  Utilisation de caches
-  Suivi des modifications dans ADE

Fonctionnalités
---------------

Frontend
++++++++

-  Personnalisation
-  Affichage calendrier
   -  mois
   -  semaine
   -  jour

-  Affichage liste d’évènements

Backend
+++++++

-  Exposition des listes de ressources
-  Exposition de la personnalisation d’un utilisateur avec un JWT
   personnel
-  Exposition des données d’emploi du temps d’un utilisateur avec un JWT
   personnel (donc correspondant aux ressources sélectionnées par
   l’utilisateur)
-  Exposition des données d’emploi du temps d’un utilisateur avec un
   UUID personnel

Données
+++++++

-  Les modifications ADE sont intégrées toutes les 5 minutes dans
   l’application. En fonction du volume à traiter, la visibilité de la
   modification pourra prendre jusqu’à 30 minutes.
-  Les salles d’enseignement contiennent la hiérarchie ADE des lieux
   (donc aussi le campus et le bâtiment)

À venir
+++++++

-  Ajout d’un plan *openstreetmap* pointant sur le bâtiment hébergeant
   la salle de cours
-  Mise à disposition d’un ICS local :

   -  rapide (hébergement S3 unistra)
   -  contenant l’intégralité des événements pour les ressources
      sélectionnées, sur l’ensemble de l’année
   -  enrichi (contiendra les bâtiments liés aux salles)

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

Redis
+++++

Un serveur Redis permet d'améliorer les performances pour les utilisateurs finaux.

Voici un exemple avec *Docker*, en mode *Least Frequently Used* pour la gestion de l'espace :

*redis.conf* :

.. code::

    maxmemory 7gb
    maxmemory-policy allkeys-lru

Dockerfile :

.. code::

    FROM redis
    COPY redis.conf /usr/local/etc/redis/redis.conf
    CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]

Construire l'image Docker :

.. code::

    docker build -t redis_lru .

Lancer le conteneur :

.. code::

    docker run -d -p 6379:6379 --shm-size 7.5g --name schedulesy-redis --rm redis_lru

.. [1]
   Uniquement dans la version poste de travail

.. [2]
   Un utilisateur peut associer un nom à un accès. Il lui sera alors
   proposé une URL directe qu’il pourra par exemple conserver en favori
   dans son navigateur. Un utilisateur peut créer autant d’accès directs
   qu’il souhaite et il peut aussi les supprimer

.. [3]
   Par exemple directement dans un élément *div* d’une page web