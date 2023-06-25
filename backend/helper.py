import re
import unicodedata

def clean_begin(string: str) -> str:
    i = string.index('1.')
    input_string = str(re.sub(r"\d+\.\s*", "", string[i:]))
    cleaned_string = ''
    for char in input_string:
        try:
            if char == '\n':
                cleaned_string += char
                continue
            # Check if the character belongs to the Latin-1 character set
            unicodedata.name(char)
            cleaned_string += char
        except ValueError:
            # If the character doesn't belong to Latin-1, skip it
            pass
    return cleaned_string

def generate_prompt(info, string):
    subject = info['Subject']
    lesson_title = info['Lesson title']
    lesson_grade = info['Grade']
    lesson_grade = info['Grade']
    duration = info['Duration']
    return f"Consider yourself a {subject} teacher suggests for teaching the topic {lesson_title} for grade {lesson_grade} students for a class that has duration of {duration} minutes" + string

