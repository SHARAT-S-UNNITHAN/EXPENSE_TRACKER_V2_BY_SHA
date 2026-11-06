from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.mail import send_mail

from .models import Goal
from .forms import GoalForm, AddAmountForm


@login_required(login_url='/authentication/login')
def add_goal(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.owner = request.user
            goal.save()
            messages.success(request, 'Goal added successfully.')
            return redirect('list_goals')
    else:
        form = GoalForm()
    return render(request, 'goals/add_goals.html', {'form': form})


@login_required(login_url='/authentication/login')
def list_goals(request):
    goals = Goal.objects.filter(owner=request.user)
    return render(
        request,
        'goals/list_goals.html',
        {'goals': goals, 'add_amount_form': AddAmountForm()}
    )


@login_required(login_url='/authentication/login')
@require_POST
def add_amount(request, goal_id):
    goal = get_object_or_404(Goal, pk=goal_id, owner=request.user)
    form = AddAmountForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Please enter a valid amount.')
        return redirect('list_goals')

    additional_amount = form.cleaned_data['additional_amount']
    amount_required = goal.amount_to_save - goal.current_saved_amount
    if additional_amount <= 0:
        messages.error(request, 'The amount must be greater than zero.')
    elif additional_amount > amount_required:
        messages.error(request, f'The maximum amount needed to achieve this goal is {amount_required}.')
    else:
        goal.current_saved_amount += additional_amount
        if goal.current_saved_amount == goal.amount_to_save:
            send_congratulatory_email(request.user.email, goal)
            goal.delete()
            messages.success(request, 'Congratulations! You have achieved your goal.')
        else:
            goal.save()
            messages.success(request, f'Amount successfully added. Total saved amount: {goal.current_saved_amount}.')
            messages.info(request, f'Amount required to reach goal: {amount_required - additional_amount}.')
    return redirect('list_goals')


def send_congratulatory_email(email, goal):
    subject = 'Congratulations on achieving your goal!'
    message = (
        f'Dear User,\\n\\nCongratulations on achieving your goal "{goal.name}". '
        f'You have successfully saved {goal.amount_to_save}.\\n\\n'
        'Keep up the good work!\\n\\nBest regards,\\nThe Goal Tracker Team'
    )
    if email:
        send_mail(subject, message, None, [email], fail_silently=True)


@login_required(login_url='/authentication/login')
@require_POST
def delete_goal(request, goal_id):
    goal = get_object_or_404(Goal, pk=goal_id, owner=request.user)
    goal.delete()
    messages.success(request, 'Goal deleted successfully.')
    return redirect('list_goals')
