export interface Alerte {
  id: number;
  anomalie_id: number;
  titre: string;
  message: string;
  niveau: 'faible' | 'moyen' | 'eleve' | 'critique';
  montant_concerne?: number;
  entite_concernee?: string;
  statut: 'non_lue' | 'lue' | 'traitee' | 'archivee';
  est_lue: boolean;
  created_at: string;
}
