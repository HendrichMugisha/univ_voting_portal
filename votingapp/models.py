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
    
    def __str__(self):
        return f"{self.name} ({self.election.name})"



# ----------------- candidate model --------------------------------
class Candidate(models.Model):
    
    # this is the position the candidate is standing for
    position = models.ForeignKey(Position, related_name="candidates", on_delete=models.CASCADE)
    
    # this is then name of the candidate
    name = models.CharField(max_length=100)
    
    # simple bio of the candidate
    bio = models.TextField(blank=True)
    
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
