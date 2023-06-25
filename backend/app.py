from config import OPENAI_API_KEY
from pdf_gen import create_lesson_plan_pdf
import openai
# from fpdf import FPDF
from flask import Flask, request, send_file
from flask_cors import CORS
from session_handler import Session_Handler
from helper import *
from datetime import datetime

app = Flask(__name__)
openai.api_key = OPENAI_API_KEY
CORS(app, resources={r"/*": {"origins": ["*"]}})
CORS(app, origins='*', methods=['GET', 'POST', 'PUT', 'DELETE'])
global_sessions = Session_Handler()

def generate_text(input_text, max_tokens=1000):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=input_text,
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=0.5,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.3,
    )
    lesson_plan = response.choices[0].text.strip()

    return lesson_plan

@app.route("/structure-plans", methods=["POST"])
def create_structure_plan():
    print(request.get_json())
    data = request.get_json()
    step_name = data['step_name'].lower()

    if step_name == 'form_submit':
        global_sessions.clean_old_sessions()
        session_id = global_sessions.create_new_session()
        lesson_title = data["lesson_title"]
        lesson_grade = data["grade"]
        # teacher_name = data["teacher_name"]
        subject = data["subject"]
        duration = data["duration_with_minutes"]
        keywords = ", ".join(data["key_words"])
        global_sessions.add_informations(session_id, {
            "Lesson title": lesson_title,
            "Teacher name": data["teacher_name"],
            "Subject": subject,
            "Grade": lesson_grade,
            "Date": datetime.now().strftime("%d/%m/%Y"),
            "Duration": f"{duration} Minutes",
            "Key vocabulary": keywords
        })

        suggestion_materials = generate_text(
            input_text=f"Consider yourself a {subject} teacher suggests for teaching the topic {lesson_title} for grade {lesson_grade} students for a class that has duration of {duration} minutes and give a suggestion for a supporting materials that can be used for example a laptop if it fit the topic {lesson_title}",
            max_tokens=30
        )
        global_sessions.add_information(
            session_id, "Supporting material", suggestion_materials)
        input_text = generate_prompt(
            global_sessions.get_session_information(session_id), "and give a numeric list of knowledges that can be covered")
        knowledges = generate_text(
            input_text=input_text,
            max_tokens=150
        )
        return {"knowledge": knowledges.split('\n'), "session_id": session_id}
        # generate suggestions for supporting materials [supporting_materials]
        # generate knowledges as list
        # return knowledges + session_id

    elif step_name == 'knowledges_submit':
        session_id = data['session_id']
        knowledges = data['knowledge']
        global_sessions.sessions[session_id]["Learning outcome"] = {
            "Knowledge": knowledges
        }

        knowledges = '\n'.join(knowledges)
        input_text = generate_prompt(
            global_sessions.get_session_information(session_id),
            f"and you want after the class gain the following knowledges:\n{knowledges}\n can you list down the skills you want them to gain along with the knowleges they will gain, please write them down as numeric"
        )
        skills = generate_text(
            input_text=input_text,
            max_tokens=150
        )
        skills = clean_begin(skills)
        return {"skills": skills.split('\n')}

    elif step_name == 'skills_submit':
        session_id = data['session_id']
        skills = data['skills']
        global_sessions.sessions[session_id]["Learning outcome"]["Skills"] = skills

        knowledges = '\n'.join(
            global_sessions.sessions[session_id]['Learning outcome']['Knowledge'])
        skills = '\n'.join(skills)
        input_text = generate_prompt(
            global_sessions.get_session_information(session_id),
            f"and you want after the class gain the following knowledges:\n{knowledges}\nand be proficient with the following skills: \n{skills}\n write down the concepts you want your students to understand, please write them down as numeric"
        )
        understanding = generate_text(
            input_text=input_text,
            max_tokens=150
        )
        understanding = clean_begin(understanding)
        return {"understanding": understanding.split('\n')}

    elif step_name == 'understanding_submit':
        session_id = data['session_id']
        understanding = data['understanding']
        global_sessions.sessions[session_id]["Learning outcome"]["Understanding"] = understanding
        session_info = global_sessions.get_session_information(session_id)
        knowledges = '\n'.join(
            global_sessions.sessions[session_id]['Learning outcome']['Knowledge'])
        skills = '\n'.join(
            global_sessions.sessions[session_id]['Learning outcome']['Skills'])
        differentiation = {
            key: generate_text(generate_prompt(
                session_info, f"and you want the students to gain the following skills \n{knowledges}\n and you want to teach it For visual learners write down some methodologies you will follow or use to explain to them, please write it as one line without numeric points, and speak in third person pronounce"), 50)
            for key in ["For visual learners", "For auditory learners", "For students with reading difficulties", "For advanced learners"]

        }
        global_sessions.add_information(
            session_id, "Differentiation", differentiation)
        input_text = generate_prompt(
            session_info,
            f"and you want the class to gain the following knowledges:\n{knowledges}\nand be proficient with the following skills: \n{skills}\n write down steps you will follow to prepare them for that, understand, please write them down as numeric"
        )
        prepare = generate_text(
            input_text=input_text,
            max_tokens=150
        )
        print(prepare)
        prepare = clean_begin(prepare)
        print(prepare)
        return {"prepare": prepare.split('\n')}

    elif step_name == 'prepare_submit':
        session_id = data['session_id']
        prepare = data['prepare']
        global_sessions.sessions[session_id]["Learning experiences"] = {
            "Prepare": prepare
        }

        knowledges = '\n'.join(
            global_sessions.sessions[session_id]['Learning outcome']['Knowledge'])
        skills = '\n'.join(
            global_sessions.sessions[session_id]['Learning outcome']['Skills'])
        understand = '\n'.join(
            global_sessions.sessions[session_id]['Learning outcome']['Understanding'])
        input_text = generate_prompt(
            global_sessions.get_session_information(session_id),
            f"and you want after the class gain the following knowledges:\n{knowledges}\nand be proficient with the following skills: \n{skills}\n also you want them to understand the following concepts:\n{understand}\n write down the steps you will take to do this class, please write them down as numeric"
        )
        plan = generate_text(
            input_text=input_text,
            max_tokens=150
        )
        plan = clean_begin(plan)
        global_sessions.sessions[session_id]['Learning experiences']['Plan'] = plan.split(
            '\n')
        input_text = generate_prompt(
            global_sessions.get_session_information(session_id),
            f"and you want after the class gain the following knowledges:\n{knowledges}\nand be proficient with the following skills: \n{skills}\n and the plan steps for the class as follow:\n{plan}\n write down a steps on how you will make student investigate the things they want to know, please write them down as numeric"
        )
        investiage = generate_text(
            input_text=input_text,
            max_tokens=150
        )
        investiage = clean_begin(investiage)
        return {"investiage": investiage.split('\n')}

    elif step_name == 'investiage_submit':
        session_id = data['session_id']
        investiage = data['investiage']
        groups = 5
        # global_sessions.add_information(session_id, "groups", groups)
        global_sessions.sessions[session_id]["Learning outcome"]["Investigate"] = investiage
        knowledges = '\n'.join(
            global_sessions.sessions[session_id]['Learning outcome']['Knowledge'])
        skills = '\n'.join(
            global_sessions.sessions[session_id]['Learning outcome']['Skills'])
        understand = '\n'.join(
            global_sessions.sessions[session_id]['Learning outcome']['Understanding'])

        plan = global_sessions.sessions[session_id]["Learning experiences"]['Plan']
        input_text = generate_prompt(
            global_sessions.get_session_information(session_id),
            f"and you want after the class gain the following knowledges:\n{knowledges}\nand be proficient with the following skills: \n{skills}\n and the plan steps for the class as follow:\n{plan}\n and you have {groups} groups write down activity for each group, please write them down as numeric"
        )
        apply = generate_text(
            input_text=input_text,
            max_tokens=150
        )
        apply = clean_begin(apply)
        apply = apply.split('\n')
        global_sessions.sessions[session_id]['Learning outcome']['Apply'] = apply

        input_text = generate_prompt(
            global_sessions.get_session_information(session_id),
            f"and you want after the class gain the following knowledges:\n{knowledges}\nand be proficient with the following skills: \n{skills}\n and the plan steps for the class as follow:\n{plan}\n write down some questions that can be used as home work, please write them down as numeric"
        )
        hw = generate_text(
            input_text=input_text,
            max_tokens=150
        )
        hw = clean_begin(hw)
        hw = hw.split('\n')
        global_sessions.sessions[session_id]['Learning experiences']['Connect'] = hw
        plan = global_sessions.sessions[session_id]["Learning experiences"]["Plan"]

        input_text = generate_prompt(
            global_sessions.get_session_information(session_id),
            f"and you want after the class gain the following knowledges:\n{knowledges}\nand be proficient with the following skills: \n{skills}\n and the plan steps for the class as follow:\n{plan}\n and the class is finished write down some ways to enhance the next class, please write them down as numeric"
        )
        enhance = generate_text(
            input_text=input_text,
            max_tokens=150
        )
        enhance = clean_begin(enhance)
        enhance = enhance.split('\n')
        global_sessions.sessions[session_id]["Educator reflection"] = enhance

        input_text = generate_prompt(
            global_sessions.get_session_information(session_id),
            f"and you want after the class gain the following knowledges:\n{knowledges}\nand be proficient with the following skills: \n{skills}\n and the plan steps for the class as follow:\n{plan}\n write down some questions that can be used as quiz, please write them down as numeric"
        )
        quiz = generate_text(
            input_text=input_text,
            max_tokens=150
        )
        quiz = clean_begin(quiz)
        quiz = quiz.split('\n')
        global_sessions.sessions[session_id]['Educator assessment'] = quiz

        input_text = generate_prompt(
            global_sessions.get_session_information(session_id),
            f"and you want after the class gain the following knowledges:\n{knowledges}\nand be proficient with the following skills: \n{skills}\n and the plan steps for the class as follow:\n{plan}\n write down some ways you will do to make the student check what they learnt , please write them down as numeric and speak in third person pronoun"
        )
        checking_students = generate_text(
            input_text=input_text,
            max_tokens=150
        )
        checking_students = clean_begin(checking_students)
        checking_students = checking_students.split('\n')
        global_sessions.sessions[session_id]["Learning experiences"]["Evaluate and reflect"] = checking_students
        create_lesson_plan_pdf(global_sessions.sessions[session_id])
        return send_file("lesson_plan.pdf", as_attachment=True)
