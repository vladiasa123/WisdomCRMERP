{
    "name": "HR Employee Evaluation (1–5)",
    "version": "18.0.1.0.0",
    "depends": ["hr"],
    "data": [
        "security/ir.model.access.csv",
        "data/evaluation_questions.xml",   # your questions
        "data/evaluation_questions_lead.xml", # lead-specific questions
        "views/hr_employee_evaluation_views.xml",
        "views/hr_employee_views.xml",     # smartbutton
    ],
    "license": "LGPL-3",
    "installable": True,
}
