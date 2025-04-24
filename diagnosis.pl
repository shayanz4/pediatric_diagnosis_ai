:- dynamic has_symptom/2.

% Diagnosis rules
diagnosis(flu) :-
    has_symptom(fever, F), F >= 3,
    has_symptom(cough, C), C >= 3,
    has_symptom(fatigue, T), T >= 2.

diagnosis(common_cold) :-
    has_symptom(runny_nose, R), R >= 2,
    has_symptom(cough, C), C >= 1.

diagnosis(measles) :-
    has_symptom(rash, R), R >= 3,
    has_symptom(fever, F), F >= 2.
