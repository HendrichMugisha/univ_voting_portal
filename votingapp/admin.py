from django.contrib import admin
from .models import StudentProfile, Election, Position, Candidate, Vote, Party

# --- 1. Student Profile Admin (The most important one) ---
class StudentProfileAdmin(admin.ModelAdmin):
    # This adds the nice "Arrow" interface for the ManyToMany field
    filter_horizontal = ('voted_in_elections',)
    
    # This shows columns in the list view
    list_display = ('user', 'student_id', 'gender', 'sponsorship_type', 'session_category', 'is_eligible')
    
    # This adds filter sidebars on the right
    list_filter = ('is_eligible', 'gender', 'sponsorship_type', 'session_category')
    
    # This adds a search bar at the top
    search_fields = ('user__username', 'student_id')

# --- 2. Position Admin ---
class PositionAdmin(admin.ModelAdmin):
    # Show the rules in the list view
    list_display = ('name', 'election', 'limit_by_gender', 'limit_by_sponsorship', 'limit_by_session')
    list_filter = ('election',)

# --- 3. Candidate Admin ---
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'party')
    list_filter = ('position__election', 'party')
    search_fields = ('name',)

# --- Register Models with Custom Classes ---
admin.site.register(StudentProfile, StudentProfileAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Candidate, CandidateAdmin)

# --- Register Basic Models ---
admin.site.register(Election)
admin.site.register(Vote)
admin.site.register(Party)