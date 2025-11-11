# link to django models module
from django.db import models
# link to settings.py 
from django.conf import settings

# demopass123

# -----------------student profile model---------------

class StudentProfile(models.Model):
    # this ensures one student can have only one profile and vice versa
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True, db_index=True)
   
    is_eligible = models.BooleanField(default=True)
   
#    allowing for gender choice so we can present each student with the relevant positions on the ballot
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)

# according to sponsorship types
    SPONSORSHIP_CHOICES = [
        ('Government', 'Government'),
        ('Private', 'Private'),
    ]
    
    sponsorship_type = models.CharField(max_length=20, choices=SPONSORSHIP_CHOICES, blank=True, null=True)

# whether they are a weekday or weekend student
    SESSION_CHOICES = [
        ('Weekend', 'Weekend_Students'),
        ('Weekday', 'Weekday_Students')
    ]
    
    session_category = models.CharField(max_length=30, choices=SESSION_CHOICES, blank=True, null=True)
    
    
    
    voted_in_elections = models.ManyToManyField(
        # this election is a string due to the forward referencing standard
        'Election', 
        blank=True, 
        related_name="voters"
    )
    
    def __str__(self):
        return self.user.username


# ----------------Elections model----------------------------------------
class Election(models.Model):
    
    # basic info about the election
    name = models.CharField(max_length=100) # e.g., "Guild Election 2026"
    description = models.TextField(blank=True)
    
    # these will be useful to start and close the election
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.name

# --- Position the candidate is standing for -------------
class Position(models.Model):
    # relates to the election in question
    election = models.ForeignKey(Election, related_name="positions", on_delete=models.CASCADE)
    
    # position name
    name = models.CharField(max_length=100) 
    
    # description of the position
    description = models.TextField(blank=True)
    
    # --------- LIMITS BASED ON CONDITION------
    limit_by_gender = models.CharField(
        max_length=10, 
        choices=StudentProfile.GENDER_CHOICES, 
        blank=True, 
        null=True
    )
    
    # limit by the scholarship type
    limit_by_sponsorship = models.CharField(
        max_length=20, 
        choices=StudentProfile.SPONSORSHIP_CHOICES, 
        blank=True, 
        null=True
    )
    
    # limit by session(weekend or weekday)
    limit_by_session = models.CharField(max_length=20, 
        choices=StudentProfile.SESSION_CHOICES, 
        blank=True, 
        null=True
        )
    
    
    def __str__(self):
        return f"{self.name} ({self.election.name})"



# ----------------- candidate model --------------------------------
class Candidate(models.Model):
    
    # this is the position the candidate is standing for
    position = models.ForeignKey(Position, related_name="candidates", on_delete=models.CASCADE)
    
    # this is then name of the candidate
    name = models.CharField(max_length=100)
    
    # photo of the candidate
    candidate_photo = models.ImageField(
        upload_to='candidate_photos/', 
        blank=True, 
        null=True
    )
    
    # the candidate's party
    party = models.ForeignKey(
        'Party', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True
    )
    
    # if the candidate is independent then they can submit their own symbol
    independent_symbol = models.ImageField(upload_to='independent_symbols/', 
        blank=True, 
        null=True)
    
    # simple bio of the candidate
    bio = models.TextField(blank=True)
    # not required anymore
    
    def __str__(self):
        return f"{self.name} for ({self.position.name})"
    


# ---------------------- this is the vote counting model ----
class Vote(models.Model):
    # this is a many to one link ie many votes can belong to one candidate
    candidate = models.ForeignKey(Candidate, related_name="votes", on_delete=models.CASCADE)
    
    # many votes can belong to one position
    position = models.ForeignKey(Position, related_name="votes", on_delete=models.CASCADE)
    
    # the time the vote was cast
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # there is no link between the vote and the student that cast it! 


# ---------- the party model --------
PARTY_CHOICES = [
    ('NRM', 'National Resistance Movement'),
    ('NUP', 'National Unity Platform'),
    ('FDC', 'Forum for Democratic Change'),
    ('DP', 'Democratic Party'),
    ('UPC', "Uganda People's Congress"),
    ('JEEMA', "Justice Forum"),
    ('PPP', "People's Progressive Party"),
    ('ANT', "Alliance for National Transformation"),
]

class Party(models.Model):
    name = models.CharField(max_length=100, unique=True, choices=PARTY_CHOICES)
    logo = models.ImageField(upload_to = 'party_logos/', blank=True, null=True
                             )
    
    def __str__(self):
        return f"{self.name}"