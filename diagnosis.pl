:- dynamic user_response/2.
:- dynamic has_symptom/2.

% Tier 1: Preliminary Symptoms
preliminary_symptom(fever).
preliminary_symptom(cough).
preliminary_symptom(runny_nose).
preliminary_symptom(rash).
preliminary_symptom(vomiting_or_diarrhea).

% Tier 2: Adaptive Symptoms
adaptive_symptom(fever, [high_grade_fever, persistent_fever, chills]).
adaptive_symptom(cough, [dry_cough, wheezing, worsens_at_night]).
adaptive_symptom(rash, [itchy_rash, rash_after_fever, rash_localized_or_widespread]).
adaptive_symptom(vomiting_or_diarrhea, [blood_in_stool, dehydration_signs, exposure_to_similar]).
adaptive_symptom(runny_nose, [runny_nose_intensity]).

% Tier 3: Deep Differentiating Symptoms
tier3_trigger([fever, rash], [measles_path, strawberry_tongue, chickenpox_blisters]).
tier3_trigger([cough, fever, wheezing], [labored_breathing, barking_cough]).
tier3_trigger([vomiting_or_diarrhea, fatigue], [travel_food_history, sluggishness]).

% Diagnosis Rules
diagnosis(measles) :-
    has_symptom(fever, _),
    has_symptom(rash, _),
    user_response(measles_path, yes).

diagnosis(roseola) :-
    has_symptom(fever, _),
    has_symptom(rash, _),
    user_response(rash_after_fever, yes).

diagnosis(chickenpox) :-
    has_symptom(rash, _),
    user_response(chickenpox_blisters, yes).

diagnosis(scarlet_fever) :-
    has_symptom(fever, _),
    has_symptom(rash, _),
    user_response(strawberry_tongue, yes).

diagnosis(flu) :-
    has_symptom(fever, _),
    user_response(high_grade_fever, yes),
    user_response(persistent_fever, yes),
    user_response(chills, yes).

diagnosis(bronchitis) :-
    has_symptom(cough, _),
    user_response(wheezing, yes),
    user_response(worsens_at_night, yes).

diagnosis(rsv) :-
    has_symptom(fever, _),
    has_symptom(cough, _),
    user_response(wheezing, yes).

