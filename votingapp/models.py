from django.db import models

# models.py
from django.db import models
from django.conf import settings

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True, db_index=True)
    is_eligible = models.BooleanField(default=True)
    
    # --- THIS IS THE CRITICAL CHANGE ---
    # We remove the old 'has_voted_guild_2025' boolean field and
    # replace it with this ManyToManyField.
    # This creates a list of all elections a user has participated in.
    voted_in_elections = models.ManyToManyField(
        'Election', 
        blank=True, 
        related_name="voters"
    )

    def __str__(self):
        return self.user.username

class Election(models.Model):
    name = models.CharField(max_length=100) # e.g., "Guild Election 2025"
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.name

# --- No changes to Position, Candidate, or Vote models ---
class Position(models.Model):
    election = models.ForeignKey(Election, related_name="positions", on_delete=models.CASCADE)
    name = models.CharField(max_length=100) 
    
    def __str__(self):
        return f"{self.name} ({self.election.name})"

class Candidate(models.Model):
    position = models.ForeignKey(Position, related_name="candidates", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)

class Vote(models.Model):
    candidate = models.ForeignKey(Candidate, related_name="votes", on_delete=models.CASCADE)
    position = models.ForeignKey(Position, related_name="votes", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
