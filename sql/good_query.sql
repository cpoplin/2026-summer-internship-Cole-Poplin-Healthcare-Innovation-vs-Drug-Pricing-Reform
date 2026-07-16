SET search_path TO ctgov, public;

WITH trial_workloads AS (
    SELECT 
        s.nct_id,
        COALESCE(i.name, 'Unknown Asset') as drug_name,
        i.intervention_type,
        st.enrollment,
        -- Straight integer subtraction divided by 30 days
        CASE 
            WHEN st.start_date > '2025-12-31' OR st.completion_date < '2025-01-01' THEN 0
            ELSE 
                ((LEAST(st.completion_date, '2025-12-31'::date) - GREATEST(st.start_date, '2025-01-01'::date)) / 30.0)
        END as months_in_2025
    FROM sponsors s
    JOIN studies st ON s.nct_id = st.nct_id
    -- JOIN directly to ignore trials without active drug/biological interventions
    JOIN interventions i ON st.nct_id = i.nct_id 
        -- Changed to UPPER() to catch 'DRUG' and 'BIOLOGICAL'
        AND UPPER(i.intervention_type) IN ('DRUG', 'BIOLOGICAL') 
    WHERE LOWER(s.name) LIKE '%pfizer%' 
      AND s.lead_or_collaborator = 'lead'
      -- Filter out placebo interventions so they don't skew your calculations
      AND LOWER(i.name) NOT LIKE '%placebo%'
      AND st.enrollment IS NOT NULL 
      AND st.start_date IS NOT NULL 
      AND st.completion_date IS NOT NULL
      AND UPPER(st.study_type) = 'INTERVENTIONAL'
)
SELECT 
    nct_id,
    drug_name,
    intervention_type,
    enrollment,
    months_in_2025,
    ROUND(enrollment * months_in_2025) as patient_months_2025
FROM trial_workloads
WHERE months_in_2025 > 0
ORDER BY patient_months_2025 DESC;