% Tokenize input string into a list of words
split_into_words(Str, Words) :-
    string_lower(Str, LowerStr),  % Convert to lowercase for consistent matching
    split_string(LowerStr, " ,.", "", RawWords),  % Split by spaces, commas, or periods
    exclude(==( ""), RawWords, Words).  % Remove empty strings

% Define parse_symptoms/2 which uses the DCG
parse_symptoms(Input, UniqueSymptoms) :-
    split_into_words(Input, Words),
    findall(Symptoms, phrase(sentence(Symptoms), Words), AllSymptoms),
    flatten(AllSymptoms, FlattenedSymptoms),
    sort(FlattenedSymptoms, UniqueSymptoms).

% DCG to parse sentence and find symptoms
sentence(Symptoms) --> find_symptoms(Symptoms).

find_symptoms([Symptom|Rest]) --> symptom(Symptom), find_symptoms(Rest).
find_symptoms([]) --> [].

% DCG rules for fever
symptom(high_grade_fever) --> words_before, ["high"], words_between, ["grade"], words_between, ["fever"], words_after.
symptom(persistent_fever) --> words_before, ["persistent"], words_between, ["fever"], words_after.
symptom(chills) --> words_before, ["chills"], words_after.

% DCG rules for rash
symptom(itchy_rash) --> words_before, ["itchy"], words_between, ["rash"], words_after.
symptom(localized_rash) --> words_before, ["localized"], words_between, ["rash"], words_after.
symptom(widespread_rash) --> words_before, ["widespread"], words_between, ["rash"], words_after.

% DCG rules for cough
symptom(dry_cough) --> words_before, ["dry"], words_between, ["cough"], words_after.
symptom(wheezing) --> words_before, ["wheezing"], words_after.
symptom(night_cough) --> words_before, ["cough"], words_between, ["worse"], words_between, ["at"], words_between, ["night"], words_after.

% Allow unrelated words to appear before, between, or after symptoms
words_before --> [].
words_before --> [_], words_before.

words_between --> [].
words_between --> [_], words_between.

words_after --> [].
words_after --> [_], words_after.