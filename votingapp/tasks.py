# from celery import shared_task
# from .models import Vote, Candidate, Position
# import logging

# # Set up a logger for this task
# log = logging.getLogger(__name__)

# @shared_task
# def process_vote_task(vote_data):
#     """
#     Receives vote data (a dict of {position_id: candidate_id})
#     and saves it to the anonymous Vote table.
    
#     This runs in the background, so it doesn't slow down the user.
#     """
#     votes_to_create = []
    
#     # We will validate the IDs to make sure they are real
#     try:
#         for position_id, candidate_id in vote_data.items():
#             # You could add more validation here, but for now
#             # we just prepare the Vote object.
#             votes_to_create.append(
#                 Vote(
#                     position_id=position_id,
#                     candidate_id=candidate_id
#                 )
#             )

#         # Use bulk_create: This is the most efficient way to save
#         # multiple objects. It performs ONE database query, not one 
#         # query per vote.
#         if votes_to_create:
#             Vote.objects.bulk_create(votes_to_create)
#             log.info(f"Successfully processed {len(votes_to_create)} votes.")
#             return f"Successfully processed {len(votes_to_create)} votes."
#         else:
#             log.warning("process_vote_task received empty vote_data.")
#             return "No votes to process."
            
#     except Exception as e:
#         # If something goes wrong, log the error.
#         # This is critical for a background task.
#         log.error(f"Error in process_vote_task: {e} with data: {vote_data}")
#         # You could also set up a retry policy here.
#         return f"Error: {e}"