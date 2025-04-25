% Tokenize input string into a list of words
split_into_words(Str, Words) :-
    string_lower(Str, LowerStr),
    split_string(LowerStr, " ,.", "", RawWords),
    exclude(==( ""), RawWords, Words).

% Parse symptoms into structured format
parse_symptoms(Input, UniqueSymptoms) :-
    split_into_words(Input, Words),
    findall(Symptoms, phrase(sentence(Symptoms), Words), AllSymptoms),
    flatten(AllSymptoms, FlattenedSymptoms),
    sort(FlattenedSymptoms, UniqueSymptoms).

% DCG for parsing input
sentence(Symptoms) --> find_symptoms(Symptoms).
find_symptoms([Symptom|Rest]) --> symptom(Symptom), find_symptoms(Rest).
find_symptoms([]) --> [].

% Tier 1: Primary Symptoms
symptom(fever) --> words_before, (["fever"] ; ["fevers"] ; ["feverish"] ; ["temperature"]), words_after.
symptom(cough) --> words_before, (["cough"] ; ["coughing"]), words_after.
symptom(rash) --> words_before, (["rash"] ; ["rashes"] ; ["skin", "outbreak"]), words_after.
symptom(vomiting) --> words_before, (["vomit"] ; ["vomiting"] ; ["throwing", "up"]), words_after.
symptom(diarrhea) --> words_before, (["diarrhea"] ; ["loose", "stool"]), words_after.
symptom(runny_nose) --> words_before, (["runny", "nose"] ; ["nasal", "discharge"]), words_after.
symptom(fatigue) --> words_before, (["fatigue"] ; ["tired"] ; ["exhausted"]), words_after.

% Tier 2: Fever-related symptoms
symptom(high_grade_fever) --> words_before, (["high", "fever"] ; ["high", "grade", "fever"]), words_after.
symptom(persistent_fever) --> words_before, (["persistent", "fever"] ; ["continuous", "fever"]), words_after.
symptom(chills) --> words_before, ["chills"], words_after.
symptom(night_sweats) --> words_before, (["night", "sweats"] ; ["sweating", "at", "night"]), words_after.

% Tier 2: Cough-related symptoms
symptom(dry_cough) --> words_before, (["dry", "cough"] ; ["non", "productive", "cough"]), words_after.
symptom(wheezing) --> words_before, (["wheezing"] ; ["wheeze"]), words_after.
symptom(worsens_at_night) --> words_before, (["worse", "at", "night"] ; ["worsens", "at", "night"]), words_after.
symptom(productive_cough) --> words_before, (["productive", "cough"] ; ["wet", "cough"] ; ["phlegm"]), words_after.
symptom(barking_cough) --> words_before, (["barking", "cough"] ; ["seal", "like", "cough"]), words_after.

% Tier 2: Rash-related symptoms
symptom(itchy_rash) --> words_before, (["itchy", "rash"] ; ["itching", "rash"]), words_after.
symptom(rash_after_fever) --> words_before, (["rash", "after", "fever"] ; ["post", "fever", "rash"]), words_after.
symptom(peeling_skin) --> words_before, (["peeling", "skin"] ; ["skin", "peeling"]), words_after.
symptom(chickenpox_blisters) --> words_before, (["blisters"] ; ["fluid", "filled", "blisters"]), words_after.

% Tier 2: GI-related symptoms
symptom(nausea) --> words_before, (["nausea"] ; ["nauseated"] ; ["feels", "sick"]), words_after.
symptom(dehydration_signs) --> words_before, (["dehydration"] ; ["dehydrated"]), words_after.
symptom(abdominal_cramps) --> words_before, (["stomach", "cramps"] ; ["abdominal", "pain"]), words_after.
symptom(watery_stool) --> words_before, (["watery", "stool"] ; ["watery", "diarrhea"]), words_after.

% Tier 2: Respiratory symptoms
symptom(nasal_congestion) --> words_before, (["congestion"] ; ["stuffy", "nose"]), words_after.
symptom(sneezing) --> words_before, ["sneezing"], words_after.
symptom(post_nasal_drip) --> words_before, (["post", "nasal", "drip"] ; ["dripping", "throat"]), words_after.
symptom(labored_breathing) --> words_before, (["difficulty", "breathing"] ; ["labored", "breathing"]), words_after.

% Tier 3: Disease-specific symptoms
symptom(measles_path) --> words_before, (["face", "to", "trunk"] ; ["spreading", "rash"]), words_after.
symptom(strawberry_tongue) --> words_before, (["strawberry", "tongue"] ; ["red", "tongue"]), words_after.
symptom(sinus_pressure) --> words_before, (["sinus", "pressure"] ; ["facial", "pressure"]), words_after.
symptom(seasonal_triggers) --> words_before, (["seasonal"] ; ["seasonal", "symptoms"]), words_after.

% Common symptom patterns for specific diseases
symptom(flu_like) --> words_before, (["flu", "like"] ; ["influenza", "like"]), words_after.
symptom(ear_pain) --> words_before, (["ear", "pain"] ; ["earache"]), words_after.
symptom(sore_throat) --> words_before, (["sore", "throat"] ; ["throat", "pain"]), words_after.
symptom(swollen_glands) --> words_before, (["swollen", "glands"] ; ["lymph", "nodes"]), words_after.
symptom(eye_redness) --> words_before, (["red", "eye"] ; ["eye", "redness"]), words_after.
symptom(eye_discharge) --> words_before, (["eye", "discharge"] ; ["goopy", "eyes"]), words_after.
symptom(body_aches) --> words_before, (["body", "aches"] ; ["muscle", "pain"]), words_after.

% Helper rules
words_before --> [].
words_before --> [_], words_before.

words_after --> [].
words_after --> [_], words_after.

% Dynamic predicates for tracking symptoms and responses
:- dynamic has_symptom/2.
:- dynamic user_response/2.

% Symptom categories
preliminary_symptom(fever).
preliminary_symptom(cough).
preliminary_symptom(rash).
preliminary_symptom(vomiting).
preliminary_symptom(diarrhea).
preliminary_symptom(runny_nose).
preliminary_symptom(fatigue).

% Adaptive symptom groups
adaptive_symptoms(fever, [high_grade_fever, persistent_fever, chills, night_sweats]).
adaptive_symptoms(cough, [dry_cough, wheezing, worsens_at_night, productive_cough, barking_cough]).
adaptive_symptoms(rash, [itchy_rash, rash_after_fever, peeling_skin, chickenpox_blisters]).
adaptive_symptoms(vomiting, [nausea, dehydration_signs]).
adaptive_symptoms(diarrhea, [watery_stool, abdominal_cramps]).
adaptive_symptoms(runny_nose, [nasal_congestion, sneezing, post_nasal_drip]).

% Helper predicate to count adaptive symptoms
count_adaptive_symptoms(Primary, Count) :-
    adaptive_symptoms(Primary, List),
    findall(S, (member(S, List), has_symptom(S, _)), Matches),
    length(Matches, Count).

% Diagnosis predicate
diagnosis(Disease) :-
    disease_rule(Disease).

% Disease rules with confidence scoring
disease_rule(measles) :-
    has_symptom(fever, _),
    has_symptom(rash, _),
    has_symptom(measles_path, _),
    user_response(fever_rash_detail, 'y').  % Face to trunk progression

disease_rule(scarlet_fever) :-
    has_symptom(fever, _),
    has_symptom(rash, _),
    user_response(fever_rash_detail, 'y'),  % Strawberry tongue
    user_response(fever_detail, High),
    (High = 'high' ; High = 'high-grade').

disease_rule(roseola) :-
    has_symptom(fever, _),
    has_symptom(rash, _),
    has_symptom(rash_after_fever, _).

disease_rule(chickenpox) :-
    has_symptom(fever, _),
    has_symptom(rash, _),
    has_symptom(chickenpox_blisters, _).

% Add helper predicate to check symptom severity
symptom_severity(Symptom, Severity) :-
    user_response(Symptom, Detail),
    atomic_list_concat([Symptom, '_detail'], Atom),
    user_response(Atom, Detail).

% Add symptom pattern rules for specific details
extract_severity(Detail, high) :- 
    sub_string(Detail, _, _, _, "high").
extract_severity(Detail, severe) :- 
    sub_string(Detail, _, _, _, "severe").