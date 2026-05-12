# Severity Scoring and Clinical Risk Stratification

Severity scoring systems quantify disease acuity and guide disposition decisions. This document summarizes commonly used clinical scores applicable to primary care triaging.

## CURB-65 Score (Community-Acquired Pneumonia)

Used to assess severity of CAP and guide admission decision.

**Scoring** (1 point each):
- **C**onfusion (acute onset disorientation or altered mental status)
- **U**rea >7 mmol/L (>19 mg/dL)
- **R**espiratory rate ≥30 breaths/minute
- **B**lood pressure: systolic <90 mmHg or diastolic <60 mmHg
- **≥65** years of age

**Interpretation**:
- Score 0–1: Outpatient management likely appropriate
- Score 2: Consider hospitalization
- Score 3–5: Hospital admission recommended, consider ICU if score 4–5

## qSOFA Score (Sepsis)

Quick assessment for risk of poor outcome from infection (sepsis).

**Scoring** (1 point each):
- **Q**uick: Respiratory rate ≥22 breaths/minute
- **S**ystolic blood pressure ≤100 mmHg
- **A**ltered mentation (confusion, disorientation)

**Interpretation**:
- Score 0–1: Low risk of sepsis-related mortality; consider infection but may manage outpatient
- Score ≥2: Higher risk of sepsis-related mortality; strongly consider hospitalization and sepsis workup (blood cultures, lactate, imaging)

## SOFA Score (Sequential Organ Failure Assessment)

More comprehensive assessment of organ dysfunction in sepsis.

**Components** (scored 0–4 points each):
- Respiratory: PaO2/FiO2 ratio
- Coagulation: Platelet count
- Liver: Bilirubin level
- Cardiovascular: Need for vasopressor therapy and mean arterial pressure
- CNS: Glasgow Coma Scale
- Renal: Creatinine or urine output

**Interpretation**:
- Total score 0–6: Low risk
- Score 7–11: Moderate risk
- Score ≥12: High risk of mortality

## Framingham Risk Score (Cardiovascular)

Estimates 10-year risk of heart attack or coronary death in adults without prior MI.

**Variables** (men and women scored differently):
- Age
- Total cholesterol
- HDL cholesterol
- Systolic blood pressure
- Smoking status
- Diabetes

**Interpretation**:
- <5%: Low risk
- 5–7.9%: Intermediate risk
- ≥8%: High risk

## Revised Geneva Score (Pulmonary Embolism)

Predicts likelihood of PE in patients with suspected VTE.

**Clinical factors** (variables scored 0–4 points):
- Age >65
- Prior DVT or PE
- Heart rate ≥100
- Hemoglobin <13 g/dL
- Clinical signs of DVT
- Unilateral leg pain
- Hemoptysis
- Clinical impression of PE likelihood

**Interpretation**:
- Low risk (<2 points): PE unlikely; consider D-dimer
- Intermediate risk (2–6 points): PE possible; imaging (CT angiography) indicated
- High risk (>6 points): PE likely; urgent imaging and anticoagulation

## NEXUS Criteria (Cervical Spine Imaging after Head/Neck Trauma)

Identifies patients requiring C-spine imaging after trauma.

**Criteria** (imaging indicated if any present):
- High-risk mechanism (diving, high-speed motor vehicle accident, fall >10 feet)
- Focal neurologic deficit
- Midline cervical tenderness
- Altered level of consciousness (intoxication, GCS <15)
- Severe head injury

**Note**: NEXUS criteria have high sensitivity; absence of all criteria makes C-spine injury very unlikely.

## CENTOR Score (Streptococcal Pharyngitis)

Predicts likelihood of Group A Streptococcus (GAS) pharyngitis.

**Criteria** (1 point each):
- Cough absent
- Exudate present
- Fever (history of temperature >38°C or measured temperature at visit)
- Anterior cervical lymphadenopathy or tenderness
- Age 3–14 years (add 1 point); Age >44 years (subtract 1 point)

**Interpretation**:
- Score 0: ~1% risk of GAS; no testing or antibiotics recommended
- Score 1: ~5% risk; optional rapid strep test
- Score 2–3: ~15–32% risk; rapid strep test recommended
- Score 4: ~51% risk; rapid strep test recommended or empiric antibiotics if high clinical suspicion

## Charlson Comorbidity Index

Predicts mortality risk based on comorbidities.

**Conditions** (weighted points assigned):
- Myocardial infarction (1)
- Congestive heart failure (1)
- Peripheral vascular disease (1)
- Cerebrovascular disease (1)
- Dementia (1)
- COPD (1)
- Renal disease (2)
- Diabetes (1; 2 if with complications)
- Liver disease (1–3)
- Malignancy (2–6)
- AIDS/HIV (6)

**Interpretation**:
- Score 0: 0–2% 10-year mortality
- Score 1–2: 2–6% 10-year mortality
- Score 3–4: 6–15% 10-year mortality
- Score ≥5: >15% 10-year mortality

## Clinical Decision-Making in Primary Care

**Integration of severity scores**:

1. **Identify syndrome** (respiratory infection, chest pain, fever, etc.)
2. **Assess red flags** for immediately life-threatening conditions
3. **Apply relevant severity score** to quantify risk
4. **Consider patient factors** (age, comorbidities, ability to follow up, social support)
5. **Make disposition decision**:
   - Self-care with close follow-up
   - Outpatient specialist referral
   - Urgent care or ED evaluation
   - Hospital admission

**Example**: 
- 65-year-old with cough, fever, dyspnea
- CURB-65 score = 2 (age ≥65, respiratory rate 28, no other features)
- Recommendation: Consider hospitalization vs. outpatient management depending on social factors and follow-up capability

## Limitations of Scoring Systems

- Scores provide **guidance**, not absolute rules
- Clinical judgment remains essential
- Scores may not capture all relevant factors (social support, patient reliability, access to follow-up)
- Over-reliance on scores can lead to missed diagnoses or unnecessary interventions
- Scores should be combined with clinical assessment, not replace it

## Application to AREP Triage

AREP triage engine can incorporate these scores to:
- Quantify severity numerically
- Support escalation decisions with evidence-based thresholds
- Explain reasoning to patients (e.g., "Your CURB-65 score is 2, suggesting consideration for professional evaluation")
- Enhance reproducibility and consistency of recommendations across cases
