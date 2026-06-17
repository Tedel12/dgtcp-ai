import csv
import random
from datetime import datetime, timedelta

def generate_csv(filename="transactions_test.csv", count=500):
    ministeres = ["Santé", "Éducation", "Infrastructures", "Défense", "Agriculture"]
    fournisseurs = ["Entreprise A", "Société B", "Tech Solutions", "BTP Bénin", "Logistique Pro"]
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['reference', 'ministere', 'fournisseur', 'montant', 'montant_prevu', 'date_transaction'])
        
        for i in range(count):
            ministere = random.choice(ministeres)
            fournisseur = random.choice(fournisseurs)
            
            # Scénarios
            scenario = random.random()
            if scenario < 0.7:  # 70% normal
                montant = random.randint(1_000_000, 50_000_000)
                montant_prevu = montant
            elif scenario < 0.85: # 15% Trop Perçu (Anomalie !)
                montant_prevu = random.randint(10_000_000, 20_000_000)
                montant = montant_prevu * random.uniform(1.5, 3.0)
            else: # 15% Montant Inhabituel
                montant = random.randint(100_000_000, 500_000_000)
                montant_prevu = 50_000_000
                
            date_trans = datetime.now() - timedelta(days=random.randint(0, 30))
            
            writer.writerow([
                f"REF-{i:04d}",
                ministere,
                fournisseur,
                int(montant),
                int(montant_prevu),
                date_trans.strftime('%Y-%m-%d')
            ])
            
    print(f" Fichier {filename} généré avec {count} transactions.")

if __name__ == "__main__":
    generate_csv()
