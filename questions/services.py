import pickle
from django.db import transaction
from .models import Question
from reference.models import Level, Skill, QF, Category

def load_dat_from_filefield(file_field):
    """Read pickle .dat and return Python object"""
    with file_field.open("rb") as f:
        return pickle.load(f)

@transaction.atomic
def import_questions_from_dicts(records):
    """
    records = list of dicts from .dat file
    Each dict should contain:
      text, part, marks, options, correct_answer, level, skill, qf, category
    """
    created = []
    for q in records:
        level = Level.objects.filter(name=q.get("level")).first() if q.get("level") else None
        skill = Skill.objects.filter(name=q.get("skill")).first() if q.get("skill") else None
        qf = QF.objects.filter(name=q.get("qf")).first() if q.get("qf") else None
        category = Category.objects.filter(name=q.get("category")).first() if q.get("category") else None

        obj = Question.objects.create(
            text=q["text"],
            part=q["part"],                # must be A/B/C/D/E/F
            marks=q.get("marks", 1),
            options=q.get("options"),
            correct_answer=q.get("correct_answer"),
            level=level,
            skill=skill,
            qf=qf,
            category=category,
        )
        created.append(obj)
    return created
