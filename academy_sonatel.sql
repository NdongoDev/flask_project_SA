CREATE TABLE public.referentiel(
        id_ref  serial,
        nom_ref character varying (255) NOT NULL
	,CONSTRAINT referentiel_PK PRIMARY KEY (id_ref)
);

CREATE TABLE public.promotion(
        id_promo   serial,
        nom_promo  character varying(255) NOT NULL,
        date_debut date NOT NULL ,
        date_fin   date NOT NULL ,
        id_ref     integer NOT NULL
	,CONSTRAINT promotion_PK PRIMARY KEY (id_promo)

	,CONSTRAINT promotion_referentiel_FK FOREIGN KEY (id_ref) REFERENCES public.referentiel(id_ref)
);

CREATE TABLE public.apprenant(
        id_apprenant   serial,
	matricule         character varying(255) NOT NULL,
        prenom         character varying(255) NOT NULL,
        nom            character varying(255) NOT NULL,
	email            character varying(255) NOT NULL,
        date_naissance date NOT NULL ,
        adresse        character varying(255) NOT NULL,
	statut		character varying(255) NOT NULL,
        id_promo       integer NOT NULL
	,CONSTRAINT apprenant_PK PRIMARY KEY (id_apprenant)

	,CONSTRAINT apprenant_promotion_FK FOREIGN KEY (id_promo) REFERENCES public.promotion(id_promo)
);
