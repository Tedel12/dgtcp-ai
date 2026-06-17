export enum TypeAnomalie {
  MONTANT_INHABITUEL = "montant_inhabituel",
  PAIEMENT_DOUBLE = "paiement_double",
  FOURNISSEUR_SUSPECT = "fournisseur_suspect",
  TROP_PERCU = "trop_percu",
  FRACTIONNEMENT = "fractionnement",
  COMPORTEMENTAL = "comportemental",
  AUTRE = "autre",
}

export enum NiveauRisque {
  FAIBLE = "faible",
  MOYEN = "moyen",
  ELEVE = "eleve",
  CRITIQUE = "critique",
}

export enum StatutAnomalie {
  NON_TRAITE = "non_traite",
  EN_COURS = "en_cours",
  TRAITE = "traite",
  FAUX_POSITIF = "faux_positif",
}

export interface Anomalie {
  id: number;
  reference: string;
  type_anomalie: TypeAnomalie;
  niveau_risque: NiveauRisque;
  score_risque: number;
  description: string;
  recommandation?: string;
  statut: StatutAnomalie;
  detected_at: string;
  transaction_id: number;
}
