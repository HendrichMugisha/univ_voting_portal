from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .import tasks

#  importing models
from .models import StudentProfile, Election, Position, Candidate

# Importing the Celery task to handle vote tallying task
from .tasks import process_vote_task



# --- 1. Authentication Views ---------------------------------------------------

def login_view(request):
    # check if the user is tryna submit data
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # authenticate them
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # if they exist simply log them in
            login(request, user)
            # Redirect to the main voting portal after successful login
            return redirect('ballot_view')
        
        else:
            # else show an error on the template
            messages.error(request, 'Invalid username or password. Please try again.')
            
    return render(request, 'login.html')

# if the user clicks the logout button
def logout_view(request):
    # log them out
    logout(request)
    # inform them
    messages.success(request, 'You have been successfully logged out.')
    # redirect them
    return redirect('login_view')




# --- 2. Voting Portal Views -------------------------------------------------------------

@login_required(login_url='login_view') # Redirect to login if not authenticated
def ballot_view(request):

    try:
        # try creating a profile vairable for the logged in user
        profile = request.user.studentprofile
        
    except StudentProfile.DoesNotExist:
        # This handles the case where a User exists but a Profile doesn't
        messages.error(request, 'Your student profile does not exist. Contact admin.')
        # send them back since they cannot vote
        return redirect('logout_view')

    # --- Eligibility Checks ---
    if not profile.is_eligible:
        return render(request, 'ineligible.html')
        
    if profile.has_voted:
        return render(request, 'already_voted.html')

    # --- Check if Election is Active ---
    now = timezone.now()
    try:
        # Find the currently active election and store it in the election variable
        election = Election.objects.get(
            name="Guild Election 2025", # this is the name of the election
            start_time__lte=now,  # Election start time must be in the past or exactly right now
            end_time__gte=now       # Election has not ended yet
        )
    except Election.DoesNotExist:
        return render(request, 'election_inactive.html')
        
        
    # --- All checks passed! Fetch the ballot data. ---
    
    # .prefetch_related('candidates') is a huge performance optimization.
    # It gets all candidates for all positions in one extra DB query,
    # preventing thousands of queries in the template.
    positions = election.positions.prefetch_related('candidates').all()

    context = {
        'positions': positions
    }
    return render(request, 'voting_portal.html', context)


@login_required(login_url='login_view')
def cast_ballot_view(request):
 
    if request.method != 'POST':
        # If someone tries to access this URL directly, send them back
        return redirect('ballot_view')

    vote_data = {}
    
    # --- CRITICAL SECTION: Prevent Double-Voting ---
    try:
        # .atomic() ensures that this entire block either
        # completes successfully or fails completely.
        with transaction.atomic():
            
            # 1. Lock the user's profile row in the database.
            # No other request can modify this user's profile
            # until this transaction is finished.
            profile = StudentProfile.objects.select_for_update().get(user=request.user)

            # 2. Double-check if they have voted
            # (in case they clicked 'submit' in two tabs at once)
            if profile.has_voted_guild_2025:
                messages.error(request, 'Your vote has already been recorded.')
                return redirect('ballot_view')
            
            # 3. Check that the election is still active
            now = timezone.now()
            election = Election.objects.get(
                name="Guild Election 2025",
                start_time__lte=now,
                end_time__gte=now
            )
            
            # 4. Mark the user as having voted.
            profile.has_voted_guild_2025 = True
            profile.save(update_fields=['has_voted_guild_2025'])
            
            # 5. Get the vote data *after* confirming eligibility
            for key, value in request.POST.items():
                # The keys for positions are their IDs (which are numbers)
                if key.isdigit():
                    vote_data[key] = value

        # --- END OF CRITICAL SECTION ---
        # The database lock on the user's profile is now released.

    except Election.DoesNotExist:
        messages.error(request, 'The election has just closed. Your vote was not counted.')
        return redirect('ballot_view')
    except Exception as e:
        messages.error(request, f'An unexpected error occurred. Please try again. {e}')
        return redirect('ballot_view')

    # --- 6. Pass the (now verified) vote data to Celery ---
    # This task runs in the background. The user doesn't wait for it.
    process_vote_task.delay(vote_data)

    # 7. Send the user to a "Thank You" page.
    return redirect('thank_you_view')


# --- 3 After voting views------------------------------------------------------------
@login_required(login_url='login_view')
def thank_you_view(request):
    """
    A simple page to show the user after they have successfully voted.
    """
    return render(request, 'thank_you.html')