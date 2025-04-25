% Tokenize input string into a list of words
split_into_words(Str, Words) :-
    string_lower(Str, LowerStr),  % Convert to lowercase for consistent matching
    split_string(LowerStr, " ,.", "", RawWords),  % Split by spaces, commas, or periods
    exclude(==( ""), RawWords, Words).  % Remove empty strings

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

% Tier 1: Preliminary Symptoms
symptom(fever) --> words_before, ["fever"], words_after.
symptom(cough) --> words_before, ["cough"], words_after.
symptom(rash) --> words_before, ["rash"], words_after.
symptom(vomiting) --> words_before, ["vomiting"], words_after.
symptom(diarrhea) --> words_before, ["diarrhea"], words_after.
symptom(runny_nose) --> words_before, ["runny", "nose"], words_after.
symptom(fatigue) --> words_before, ["fatigue"], words_after.

% Tier 2: Adaptive Symptoms
symptom(high_grade_fever) --> words_before, ["high", "grade", "fever"], words_after.
symptom(persistent_fever) --> words_before, ["persistent", "fever"], words_after.
symptom(chills) --> words_before, ["chills"], words_after.
symptom(night_sweats) --> words_before, ["night", "sweats"], words_after.

symptom(dry_cough) --> words_before, ["dry", "cough"], words_after.
symptom(wheezing) --> words_before, ["wheezing"], words_after.
symptom(worsens_at_night) --> words_before, ["worsens", "at", "night"], words_after.
symptom(productive_cough) --> words_before, ["productive", "cough"], words_after.

symptom(itchy_rash) --> words_before, ["itchy", "rash"], words_after.
symptom(rash_after_fever) --> words_before, ["rash", "after", "fever"], words_after.
symptom(rash_localized_or_widespread) --> words_before, ["rash", "localized"], words_after.
symptom(peeling_skin) --> words_before, ["peeling", "skin"], words_after.

symptom(blood_in_vomit) --> words_before, ["blood", "in", "vomit"], words_after.
symptom(dehydration_signs) --> words_before, ["dehydration", "signs"], words_after.
symptom(exposure_to_similar) --> words_before, ["exposure", "to", "similar"], words_after.
symptom(nausea) --> words_before, ["nausea"], words_after.

symptom(frequent_loose_stools) --> words_before, ["frequent", "loose", "stools"], words_after.
symptom(abdominal_cramps) --> words_before, ["abdominal", "cramps"], words_after.
symptom(urgency_to_defecate) --> words_before, ["urgency", "to", "defecate"], words_after.
symptom(watery_stool) --> words_before, ["watery", "stool"], words_after.

symptom(runny_nose_intensity) --> words_before, ["runny", "nose", "intensity"], words_after.
symptom(nasal_congestion) --> words_before, ["nasal", "congestion"], words_after.
symptom(sneezing) --> words_before, ["sneezing"], words_after.
symptom(post_nasal_drip) --> words_before, ["post", "nasal", "drip"], words_after.

symptom(chronic_tiredness) --> words_before, ["chronic", "tiredness"], words_after.
symptom(low_energy) --> words_before, ["low", "energy"], words_after.
symptom(difficulty_concentrating) --> words_before, ["difficulty", "concentrating"], words_after.
symptom(unrefreshing_sleep) --> words_before, ["unrefreshing", "sleep"], words_after.

% Tier 3: Deep Differentiating Symptoms
symptom(measles_path) --> words_before, ["measles", "path"], words_after.
symptom(strawberry_tongue) --> words_before, ["strawberry", "tongue"], words_after.
symptom(chickenpox_blisters) --> words_before, ["chickenpox", "blisters"], words_after.

symptom(labored_breathing) --> words_before, ["labored", "breathing"], words_after.
symptom(barking_cough) --> words_before, ["barking", "cough"], words_after.
symptom(persistent_cough) --> words_before, ["persistent", "cough"], words_after.

symptom(travel_food_history) --> words_before, ["travel", "food", "history"], words_after.
symptom(contamination_exposure) --> words_before, ["contamination", "exposure"], words_after.
symptom(stomach_pain) --> words_before, ["stomach", "pain"], words_after.

symptom(prolonged_fatigue) --> words_before, ["prolonged", "fatigue"], words_after.
symptom(sinus_pressure) --> words_before, ["sinus", "pressure"], words_after.
symptom(seasonal_triggers) --> words_before, ["seasonal", "triggers"], words_after.

% Helper rules to allow unrelated words before, between, or after symptoms
words_before --> [].
words_before --> [_], words_before.

words_after --> [].
words_after --> [_], words_after.