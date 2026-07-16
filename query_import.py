text= """
    WITH trial_workloads AS (
        SELECT 
            s.nct_id,
            COALESCE(i.name, 'Unknown Asset') as drug_name,
            i.intervention_type,
            st.enrollment,
            CASE 
                WHEN st.start_date > CAST(:year_end AS date) OR st.completion_date < CAST(:year_start AS date) THEN 0
                ELSE ((LEAST(st.completion_date, CAST(:year_end AS date)) - GREATEST(st.start_date, CAST(:year_start AS date))) / 30.0)
            END as months_in_given_year
        FROM ctgov.sponsors s
        JOIN ctgov.studies st ON s.nct_id = st.nct_id
        JOIN ctgov.interventions i ON st.nct_id = i.nct_id 
            AND UPPER(i.intervention_type) IN ('DRUG', 'BIOLOGICAL') 
        WHERE LOWER(s.name) LIKE :company_match 
          AND s.lead_or_collaborator = 'lead'
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
        months_in_given_year,
        ROUND(enrollment * months_in_given_year) as patient_months_given_year
    FROM trial_workloads
    WHERE months_in_given_year > 0
    ORDER BY patient_months_given_year DESC;
"""