export enum Role {
  ADMIN = "admin",
  COMPTABLE = "comptable",
  AUDITEUR = "auditeur",
  DIRECTEUR = "directeur",
  ANALYSTE_FINANCIER = "analyste_financier",
  CONTROLEUR_FINANCIER = "controleur_financier",
}

export interface Utilisateur {
  id: number;
  nom: string;
  prenom: string;
  email: string;
  role: Role;
  poste?: string;
  avatar_url?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  utilisateur: Utilisateur;
}
