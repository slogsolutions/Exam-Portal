from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import CandidateProfile
from .forms import CandidateRegistrationForm

@login_required
def candidate_dashboard(request):
    candidate_profile = get_object_or_404(CandidateProfile, user=request.user)
    exams_scheduled = []
    upcoming_exams = []
    completed_exams = []
    results = []

    return render(request, "registration/dashboard.html", {
        "candidate": candidate_profile,
        "exams_scheduled": exams_scheduled,
        "upcoming_exams": upcoming_exams,
        "completed_exams": completed_exams,
        "results": results,
    })

def register_candidate(request):
    if request.method == "POST":
        form = CandidateRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.user = request.user   # ✅ link logged-in user
            candidate.save()
            return redirect("login")
    else:
        form = CandidateRegistrationForm()
    return render(request, "registration/register_candidate.html", {"form": form})


# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from registration.models import CandidateProfile
from centers.models import Center
from questions.models import Question, QuestionPaper, PaperQuestion
from exams.models import ExamAssignment, ExamAttempt, Shift, ExamDayAvailability
from reference.models import Category, Trade, Level, Skill, QF, Qualification
from django.utils import timezone
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@login_required
def exam_interface(request):
    try:
        # Get user profile
        profile = CandidateProfile.objects.select_related(
            'trade', 'level_of_qualification', 'nsqf_level', 
            'skill', 'qf', 'qualification', 'category', 'center'
        ).get(user=request.user)
        
        # Get exam assignment for this user
        exam_assignment = ExamAssignment.objects.select_related(
            'center', 'shift', 'primary_paper', 'common_paper'
        ).filter(
            candidate=request.user,
            status__in=['SCHEDULED', 'STARTED']
        ).first()
        
        if not exam_assignment:
            return render(request, "registration/exam_interface.html", {
                "error": "No exam assignment found for your account."
            })
        
        # Update status to STARTED if not already
        if exam_assignment.status == 'SCHEDULED':
            exam_assignment.status = 'STARTED'
            exam_assignment.save()
            
            # Create exam attempt
            exam_attempt = ExamAttempt.objects.create(
                assignment=exam_assignment,
                started_at=timezone.now()
            )
        else:
            exam_attempt = ExamAttempt.objects.get(assignment=exam_assignment)
        
        # Get questions from both papers
        primary_questions = exam_assignment.primary_paper.questions.all().order_by('paperquestion__order')
        common_questions = exam_assignment.common_paper.questions.all().order_by('paperquestion__order')
        
        # Combine questions with part information
        all_questions = []
        question_counter = 1
        
        # Add primary paper questions (Part B - Departmental)
        for question in primary_questions:
            all_questions.append({
                'id': question_counter,
                'db_id': question.id,
                'part': 'B',
                'type': question.part,
                'text': question.text,
                'options': question.options,
                'marks': float(question.marks),
                'paper_type': 'primary'
            })
            question_counter += 1
        
        # Add common paper questions (Part A - General)
        for question in common_questions:
            all_questions.append({
                'id': question_counter,
                'db_id': question.id,
                'part': 'A',
                'type': question.part,
                'text': question.text,
                'options': question.options,
                'marks': float(question.marks),
                'paper_type': 'common'
            })
            question_counter += 1
        
        # Get existing answers if any
        existing_answers = {}
        answers = exam_attempt.answers.select_related('question').all()
        for answer in answers:
            existing_answers[answer.question.id] = {
                'given': answer.given,
                'text_answer': answer.text_answer
            }
        
        # Prepare context
        context = {
            "user": request.user,
            "profile": profile,
            "center": exam_assignment.center,
            "exam_assignment": exam_assignment,
            "exam_attempt": exam_attempt,
            "questions": all_questions,
            "total_questions": len(all_questions),
            "existing_answers": json.dumps(existing_answers),
            "shift": exam_assignment.shift,
        }
        
        return render(request, "registration/exam_interface.html", context)
        
    except CandidateProfile.DoesNotExist:
        return redirect('profile_completion')
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(_name_)
        logger.error(f"Error in exam_interface: {str(e)}")
        
        return render(request, "registration/exam_interface.html", {
            "user": request.user,
            "error": f"Error loading exam: {str(e)}"
        })


@csrf_exempt
@require_POST
@login_required
def save_answer(request):
    try:
        data = json.loads(request.body)
        question_id = data.get('question_id')
        answer = data.get('answer')
        text_answer = data.get('text_answer', '')
        
        # Get exam attempt
        exam_attempt = ExamAttempt.objects.get(assignment__candidate=request.user)
        
        # Get question
        question = Question.objects.get(id=question_id)
        
        # Save or update answer
        answer_obj, created = Answer.objects.get_or_create(
            attempt=exam_attempt,
            question=question,
            defaults={
                'given': answer,
                'text_answer': text_answer
            }
        )
        
        if not created:
            answer_obj.given = answer
            answer_obj.text_answer = text_answer
            answer_obj.save()
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@csrf_exempt
@require_POST
@login_required
def submit_exam(request):
    try:
        data = json.loads(request.body)
        answers = data.get('answers', {})
        
        # Get exam attempt
        exam_attempt = ExamAttempt.objects.get(assignment__candidate=request.user)
        
        # Update all answers
        for question_id, answer_data in answers.items():
            question = Question.objects.get(id=question_id)
            
            answer_obj, created = Answer.objects.get_or_create(
                attempt=exam_attempt,
                question=question
            )
            
            answer_obj.given = answer_data.get('given')
            answer_obj.text_answer = answer_data.get('text_answer', '')
            answer_obj.save()
        
        # Mark exam as submitted
        exam_attempt.submitted_at = timezone.now()
        exam_attempt.save()
        
        # Update assignment status
        assignment = exam_attempt.assignment
        assignment.status = 'SUBMITTED'
        assignment.save()
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Exam submitted successfully',
            'submitted_at': exam_attempt.submitted_at.isoformat()
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
def user_profile_data(request):
    try:
        profile = CandidateProfile.objects.select_related(
            'trade', 'level_of_qualification', 'nsqf_level', 
            'skill', 'qf', 'qualification', 'category', 'center'
        ).get(user=request.user)
        
        return JsonResponse({
            'name': profile.name,
            'army_no': profile.army_no,
            'rank': profile.rank,
            'trade': profile.trade.name if profile.trade else '',
            'category_name': profile.category.name if profile.category else '',
            'category_id': profile.category.id if profile.category else None,
            'initials': ''.join([name[0] for name in profile.name.split()[:2]]).upper(),
        })
    except CandidateProfile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)


@login_required
def center_info(request):
    try:
        profile = CandidateProfile.objects.select_related('center').get(user=request.user)
        return JsonResponse({
            'name': profile.center.name,
            'code': profile.center.code,
            'address': profile.center.address,
        })
    except CandidateProfile.DoesNotExist:
        return JsonResponse({'error': 'Center not found'}, status=404)


def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('/accounts/login/')