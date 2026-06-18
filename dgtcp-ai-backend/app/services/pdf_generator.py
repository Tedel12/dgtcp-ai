from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
import io
from datetime import datetime

def generer_rapport_pdf(stats: dict, top_anomalies: list):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    
    # Styles personnalisés "Premium"
    style_titre = ParagraphStyle(
        'TitrePremium',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=30,
        alignment=1, # Centre
        fontName='Helvetica-Bold'
    )
    
    style_sous_titre = ParagraphStyle(
        'SousTitrePremium',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor("#3B82F6"),
        spaceBefore=20,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )

    elements = []

    # ── Header ────────────────────────────────────────────────────────────────
    elements.append(Paragraph("DGTCP-AI : INTELLIGENCE FINANCIÈRE", style_titre))
    elements.append(Paragraph(f"Rapport de Synthèse Stratégique — {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
    elements.append(Spacer(1, 0.5 * inch))

    # ── Section 1 : Indicateurs Clés ──────────────────────────────────────────
    elements.append(Paragraph("1. Indicateurs de Performance Globaux", style_sous_titre))
    
    data_kpi = [
        ["Indicateur", "Valeur"],
        ["Total des Transactions Analysées", f"{stats['total_transactions']:,} FCFA".replace(",", " ")],
        ["Anomalies Détectées", f"{stats['anomalies_detectees']}"],
        ["Économies Potentielles (Risque Élevé)", f"{stats['economies_potentielles']:,} FCFA".replace(",", " ")],
        ["Taux de Conformité", f"{stats['taux_transactions_normales']}%"]
    ]
    
    t_kpi = Table(data_kpi, colWidths=[3*inch, 2*inch])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(t_kpi)
    elements.append(Spacer(1, 0.4 * inch))

    # ── Section 2 : Anomalies Critiques (Top 5) ───────────────────────────────
    elements.append(Paragraph("2. Alertes Prioritaires (Top 5 Risques)", style_sous_titre))
    
    data_anom = [["Référence", "Type", "Ministère", "Montant (FCFA)", "Risque"]]
    for a in top_anomalies:
        data_anom.append([
            a.reference,
            a.type_anomalie.value.replace("_", " ").title(),
            a.transaction.ministere,
            f"{a.transaction.montant:,.0f}".replace(",", " "),
            f"{a.score_risque}%"
        ])

    t_anom = Table(data_anom, colWidths=[1.2*inch, 1.5*inch, 1.2*inch, 1.2*inch, 0.6*inch])
    t_anom.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F97316")), # Orange DGTCP pour les alertes
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    elements.append(t_anom)
    
    elements.append(Spacer(1, 0.4 * inch))

    # ── Section 3 : Recommandation Stratégique ────────────────────────────────
    elements.append(Paragraph("3. Recommandation du Système", style_sous_titre))
    reco_text = (
        "L'analyse prédictive indique une vigilance accrue sur les transactions de type 'Trop Perçu'. "
        "Il est recommandé de suspendre tout paiement dépassant le budget initial de plus de 15% sans "
        "avenant contractuel validé par le Contrôleur Financier."
    )
    elements.append(Paragraph(reco_text, styles['Normal']))

    # ── Footer ────────────────────────────────────────────────────────────────
    elements.append(Spacer(1, 1 * inch))
    footer_text = "Généré par DGTCP-AI — Système d'Intégration et de Contrôle Automatisé"
    elements.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=1)))

    doc.build(elements)
    buffer.seek(0)
    return buffer
