export enum StatutTransaction {
  EN_ATTENTE = "en_attente",
  VALIDE = "valide",
  REJETE = "rejete",
  PAYE = "paye",
}

export enum TypeTransaction {
  DEPENSE = "depense",
  RECETTE = "recette",
  VIREMENT = "virement",
}

export interface Transaction {
  id: number;
  reference: string;
  ministere: string;
  fournisseur: string;
  montant: number;
  montant_prevu?: number;
  type_transaction: TypeTransaction;
  statut: StatutTransaction;
  est_anomalie: boolean;
  score_risque: number;
  date_transaction: string;
  description?: string;
}
