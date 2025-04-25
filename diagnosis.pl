:- [dcg_rules].
:- dynamic user_response/2.
:- dynamic has_symptom/2.

% Tier 1: Preliminary Symptoms
preliminary_symptom(fever).
preliminary_symptom(cough).
preliminary_symptom(rash).
preliminary_symptom(vomiting).
preliminary_symptom(diarrhea).
preliminary_symptom(runny_nose).
preliminary_symptom(fatigue).


% Tier 2: Adaptive Symptoms
has_symptom_severity(Symptom, Level) :- 
    has_symptom(Symptom, _),
    user_response(Symptom, Level).

symptom_severity(high, 4..5).
symptom_severity(moderate, 2..3).
symptom_severity(mild, 0..1).

adaptive_symptom(fever, [high_grade_fever, persistent_fever, chills, night_sweats]).
adaptive_symptom(cough, [dry_cough, wheezing, worsens_at_night, productive_cough]).
adaptive_symptom(rash, [itchy_rash, rash_after_fever, rash_localized_or_widespread, peeling_skin]).
adaptive_symptom(vomiting, [blood_in_vomit, dehydration_signs, exposure_to_similar, nausea]).
adaptive_symptom(diarrhea, [frequent_loose_stools, abdominal_cramps, urgency_to_defecate, watery_stool]).
adaptive_symptom(runny_nose, [runny_nose_intensity, nasal_congestion, sneezing, post_nasal_drip]).
adaptive_symptom(fatigue, [chronic_tiredness, low_energy, difficulty_concentrating, unrefreshing_sleep]).

% Tier 3: Deep Differentiating Symptoms
tier3_trigger([fever, rash], [measles_path, strawberry_tongue, chickenpox_blisters]).
tier3_trigger([cough, fever], [labored_breathing, barking_cough, persistent_cough]).
tier3_trigger([vomiting, diarrhea], [travel_food_history, contamination_exposure, stomach_pain]).
tier3_trigger([fatigue, runny_nose], [prolonged_fatigue, sinus_pressure, seasonal_triggers]).


% Diagnosis Rules (Aligned with Tier 1, 2, and 3)

% Add helper predicate to check adaptive symptoms
has_adaptive_symptoms(PrimarySymptom, Count) :-
    adaptive_symptom(PrimarySymptom, AdaptiveList),
    findall(Symptom, (
        member(Symptom, AdaptiveList),
        user_response(Symptom, yes)
    ), Matches),
    length(Matches, Count).

% Modified diagnosis rules to use adaptive symptoms
% Measles: Fever + Rash + Measles Path
diagnosis(measles) :-
    has_symptom(fever, _),
    has_symptom(rash, _),
    has_adaptive_symptoms(fever, FeverCount),
    has_adaptive_symptoms(rash, RashCount),
    FeverCount >= 2,  % At least 2 fever-related adaptive symptoms
    RashCount >= 1,   % At least 1 rash-related adaptive symptom
    user_response(measles_path, yes).

% Roseola: Fever → Rash appears after fever
diagnosis(roseola) :-
    has_symptom(fever, _),
    has_symptom(rash, _),
    user_response(rash_after_fever, yes).

% Chickenpox: Rash + blister pattern
diagnosis(chickenpox) :-
    has_symptom(rash, _),
    user_response(chickenpox_blisters, yes).

% Scarlet Fever: Fever + Rash + strawberry tongue
diagnosis(scarlet_fever) :-
    has_symptom(fever, _),
    has_symptom(rash, _),
    user_response(strawberry_tongue, yes).

% Flu: High fever + chills + persistent fever (all Tier 2 of fever)
diagnosis(flu) :-
    has_symptom(fever, _),
    has_adaptive_symptoms(fever, Count),
    Count >= 3,  % Requires at least 3 fever-related adaptive symptoms
    user_response(high_grade_fever, yes),
    user_response(chills, yes).

% Bronchitis: Cough + wheezing + worsens at night (Tier 2 of cough)
diagnosis(bronchitis) :-
    has_symptom(cough, _),
    has_adaptive_symptoms(cough, Count),
    Count >= 2,  % At least 2 cough-related adaptive symptoms
    user_response(wheezing, yes),
    user_response(productive_cough, yes).

% RSV: Cough + Fever + wheezing (Tier 2 of cough)
diagnosis(rsv) :-
    has_symptom(fever, _),
    has_symptom(cough, _),
    user_response(wheezing, yes).

% Food poisoning: Vomiting + Diarrhea + travel/contamination exposure (Tier 3)
diagnosis(food_poisoning) :-
    has_symptom(vomiting, _),
    has_symptom(diarrhea, _),
    user_response(dehydration_signs, yes),
    user_response(frequent_loose_stools, yes),
    user_response(contamination_exposure, yes).

% Sinusitis: Runny nose + fatigue + sinus pressure (Tier 3)
diagnosis(sinusitis) :-
    has_symptom(runny_nose, _),
    has_symptom(fatigue, _),
    user_response(nasal_congestion, yes),
    user_response(sinus_pressure, yes),
    user_response(post_nasal_drip, yes).