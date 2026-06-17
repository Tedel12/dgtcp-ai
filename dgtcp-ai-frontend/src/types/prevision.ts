export interface PrevisionMensuelle {
  mois: string;
  mois_num: number;
  depenses_prevues: number;
  depenses_reelles?: number;
  recettes_prevues: number;
  recettes_reelles?: number;
  solde_previsionnel: number;
  ecart_pct?: number;
}

export interface PrevisionResponse {
  solde_actuel_fcfa: number;
  alerte_liquidite: boolean;
  mois_courant: string;
  previsions: PrevisionMensuelle[];
}

export interface RisqueBudgetaire {
  ministere: string;
  depenses_reelles_fcfa: number;
  budget_prevu_fcfa: number;
  ecart_fcfa: number;
  taux_execution_pct: number;
  niveau_risque: 'faible' | 'moyen' | 'eleve';
  nb_transactions: number;
}
