% DCG Rules for Fever Descriptions
fever_description --> [high, grade], {assert(user_response(high_grade_fever, yes))}.
fever_description --> [persistent], {assert(user_response(persistent_fever, yes))}.
fever_description --> [chills], {assert(user_response(chills, yes))}.

% DCG Rules for Rash Descriptions
rash_description --> [localized], {assert(user_response(rash_localized, yes))}.
rash_description --> [widespread], {assert(user_response(rash_widespread, yes))}.
rash_description --> [itchy], {assert(user_response(itchy_rash, yes))}.

% DCG Rules for Cough Descriptions
cough_description --> [dry], {assert(user_response(dry_cough, yes))}.
cough_description --> [wheezing], {assert(user_response(wheezing, yes))}.
cough_description --> [worsens, at, night], {assert(user_response(worsens_at_night, yes))}.

% Parsing Predicates
process_fever_input(Input) :-
    phrase(fever_description, Input).

process_rash_input(Input) :-
    phrase(rash_description, Input).

process_cough_input(Input) :-
    phrase(cough_description, Input).