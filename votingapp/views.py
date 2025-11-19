from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from functools import wraps

# importing models
from .models import StudentProfile, Election, Position, Candidate, Vote

# this is a decorator to check if the logged in user has a profile-------
def profile_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            # Check if the profile exists
            profile = request.user.studentprofile
            
            # attaching the profile to the request object so the view function doesnt even look for it
            request.profile = profile 
            
        except StudentProfile.DoesNotExist:
            # If the profile doesn't exist, log them out.
            messages.error(request, 'Your student profile does not exist. Contact admin.')
            return redirect('logout_view')
        
        # If the try block succeeds, run the original view function
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


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
            if user.is_staff:
                # log them in and send them to the results dashboard right away
                login(request, user)
                return redirect('results_dashboard')
            else:
                login(request, user)
                # Redirect to the main voting portal after successful login
                return redirect('election_list_view')
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

# ----------view for all the elections
@login_required(login_url='login_view')
@profile_required  
def election_list_view(request):
    # grab the timezone aware time
    now = timezone.now()
    
    # check for active elections
    active_elections_qs = Election.objects.filter(
        start_time__lte=now, #start time is in the past
        end_time__gte=now #end time is in the future
    ).order_by('end_time')

    # Get the list of elections the user has *already* voted in
    voted_in = request.profile.voted_in_elections.all() 
    
    # Create a list of tuples: (election, has_voted)
    active_elections_data = [
        (election, election in voted_in) 
        for election in active_elections_qs
    ]

    # this will be available to the election list template
    context = {
        'active_elections_data': active_elections_data
    }
    return render(request, 'election_list.html', context)


# ---------the ballot view for one specific election------------------------------
@login_required(login_url='login_view')
@profile_required
def ballot_view(request, election_id): #Takes election_id of the election tha has been selected by the user in the frontend
      
    now = timezone.now()
    
    # Get the specific election requested by the user, but ONLY if it's currently active
    election = get_object_or_404(
        Election,
        pk=election_id, #primary key is the election id requested by the user
        start_time__lte=now,
        end_time__gte=now
    )
    
    profile = request.profile

    # --- Eligibility Checks (For Demo)--- 
    if not profile.is_eligible:
        return render(request, 'ineligible.html')

    # Checks if the requested election is in the user's "voted_in" list
    if election in profile.voted_in_elections.all():
        return render(request, 'already_voted.html')

    # getting all the candidates for all the positions for this particular election 
    # prefetch candidates AND their parties to avoid N+1 queries
    all_positions = election.positions.prefetch_related('candidates__party').all()
    
    # creating a list that will store the positions for which the logged in user is eligible to vote
    eligible_positions = []
    
    # loop through all the positions
    for position in all_positions:
        
        # Assume they are eligible, then prove they are not
        is_eligible_for_pos = True 
        
        # 1. Check Gender Rule
        if position.limit_by_gender: 
            if position.limit_by_gender != profile.gender:
                is_eligible_for_pos = False
        
        # 2. Check Sponsorship Rule
        if is_eligible_for_pos and position.limit_by_sponsorship: 
            if position.limit_by_sponsorship != profile.sponsorship_type:
                is_eligible_for_pos = False
        
        # 3. Check Session Rule (NEW)
        if is_eligible_for_pos and position.limit_by_session:
            if position.limit_by_session != profile.session_category:
                is_eligible_for_pos = False

        # If they passed all checks, add the position to the list
        if is_eligible_for_pos:
            eligible_positions.append(position)

    # handing this information to the frontend
    context = {
        'election': election,
        'positions': eligible_positions
    }
    return render(request, 'voting_portal.html', context)


#-------------------casting the ballot----------------
@login_required(login_url='login_view')
@profile_required
def cast_ballot_view(request, election_id): #Takes election_id

    if request.method != 'POST':
        # If someone tries to access this URL directly, send them back ie, we only want post requests
        return redirect('election_list_view')

    now = timezone.now()
    
    try:
        # --- CRITICAL SECTION: if anything happens inside this code block, the db rolls back all changes
        with transaction.atomic():
            
            # 1. get the election and check if its still active
            election = get_object_or_404(
                Election,
                pk=election_id,
                start_time__lte=now,
                end_time__gte=now
            )
            
            # 2. Lock the user's profile row so nothing else touches it till the transaction is finished
            profile = StudentProfile.objects.select_for_update().get(user=request.user)

            # 3. Double-check if they have voted
            if election in profile.voted_in_elections.all():
                messages.error(request, 'Your vote has already been recorded.')
                return redirect('election_list_view')
            
            # 4. Mark the user as having voted *in this election*
            profile.voted_in_elections.add(election)
            
            # 5. get the vote data from request.post
            vote_data = {}
            for key, value in request.POST.items():
                # The keys for positions are their IDs (which are numbers)
                if key.isdigit():
                    vote_data[key] = value
                    
            # 6. --------   VOTE PROCESSING---------
            votes_to_create = []
            
            # create the vote object for the users submission
            for position_id, candidate_id in vote_data.items():
                votes_to_create.append(
                    Vote(
                        position_id=position_id,
                        candidate_id=candidate_id
                    )
                )
                
            # check if the user was a dummy and tried to submit an empty ballot
            if votes_to_create:
                # grab all the users votes for all the candidates and stamp them into the database at once
                Vote.objects.bulk_create(votes_to_create)
            else:
                raise Exception("Empty ballot submission is not allowed.")

        # --- END OF TRANSACTION ---

    except Election.DoesNotExist:
        messages.error(request, 'The election has just closed. Your vote was not counted.')
        return redirect('election_list_view')
    except Exception as e:
        messages.error(request, f'An unexpected error occurred. Please try again. {e}')
        return redirect('election_list_view')

    # 7. Send the user to a "Thank You" page.
    return redirect('thank_you_view')


# --- 3. After-Voting View ---
@login_required(login_url='login_view')
def thank_you_view(request):
    return render(request, 'thank_you.html')


# ----------------admin related views and helpers -------
def is_admin_user(user):
    # returns true only if the user is authenticated and is staff ie is an admin
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin_user, login_url='login_view')
def results_dashboard_view(request):
    # displays a list of all past and present elections that the user can then click on to see results
    elections = Election.objects.all().order_by('-start_time') #sorts them newest to oldest
    context = {
        'elections': elections
    }
    return render(request, 'admin_results_dashboard.html', context)


#------------- display reuslts to admin--------------------------
@user_passes_test(is_admin_user, login_url='login_view')
def election_results_view(request, election_id):
    
    # get the requested election by primary key
    election = get_object_or_404(Election, pk=election_id)
    
    # We get all positions for this election
    positions = election.positions.all()
    
    # We get all candidates and count how many 'votes' are related to each one.
    candidates_with_votes = Candidate.objects.filter( 
        position__election=election 
    ).annotate( # this adds a new field to each candidae object in the list
        vote_count=Count('votes')  # this says the new field will be named vote_count
    ).order_by('position', '-vote_count') # Group by position, then vote count

    # We also get the total number of voters for this election
    total_voters = election.voters.count()

    context = {
        'election': election,
        'positions': positions,
        'candidates_with_votes': candidates_with_votes,
        'total_voters': total_voters,
    }
    return render(request, 'admin_election_results.html', context)