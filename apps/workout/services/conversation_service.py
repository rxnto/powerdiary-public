# import os
# from datetime import datetime
# import json
# import logging
# from ..models import Workout, Exercise
# from django.db import transaction
# from django.core.exceptions import ObjectDoesNotExist

# logging.basicConfig(
#     filename='chat_service.log',
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )

# class ConversationService:
#     def __init__(self):
#         try:
#             current_dir = os.path.dirname(os.path.abspath(__file__))
#             app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#             self.conversations_dir = os.path.join(app_dir, 'data', 'conversations')
#             os.makedirs(self.conversations_dir, exist_ok=True)
#             logging.info('ConversationService initialized successfully')
#         except Exception as e:
#             logging.error(f'Error initializing ConversationService: {str(e)}')
#             raise
        
#     def save_conversation(self, user, content, is_user=True):
#         conversation = {
#             'user_id': user.id,
#             'content': content,
#             'is_user': is_user,
#             'timestamp': datetime.now().isoformat()
#         }
        
#         file_path = os.path.join(
#             self.conversations_dir,
#             f'conversations_{user.id}.jsonl'
#         )
        
#         with open(file_path, 'a', encoding='utf-8') as f:
#             f.write(json.dumps(conversation, ensure_ascii=False) + '\n')
            
#     def get_recent_conversations(self, user, limit=10):
#         file_path = os.path.join(
#             self.conversations_dir,
#             f'conversations_{user.id}.jsonl'
#         )
        
#         if not os.path.exists(file_path):
#             return []
            
#         conversations = []
#         with open(file_path, 'r', encoding='utf-8') as f:
#             for line in f:
#                 conversations.append(json.loads(line))
                
#         return conversations[-limit:]
    
#     def get_user_training_data(self, user):
#         try:
#             current_date = datetime.now()
#             current_year = current_date.year
#             current_month = current_date.month
            
#             training_data = []
            
#             # クエリの最適化のためにselect_relatedを使用
#             with transaction.atomic():
#                 for i in range(6):
#                     if current_month - i <= 0:
#                         year = current_year - 1
#                         month = 12 + (current_month - i)
#                     else:
#                         year = current_year
#                         month = current_month - i
                        
#                     start_date = datetime(year, month, 1)
#                     if month == 12:
#                         end_date = datetime(year + 1, 1, 1)
#                     else:
#                         end_date = datetime(year, month + 1, 1)
                    
#                     month_workouts = (Workout.objects
#                         .filter(
#                             user=user,
#                             created_at__gte=start_date,
#                             created_at__lt=end_date
#                         )
#                         .select_related('user')
#                         .prefetch_related('exercise_set')
#                         .order_by('-created_at'))
                    
#                     if month_workouts.exists():
#                         monthly_data = {
#                             'year_month': f'{year}年{month}月',
#                             'workouts': []
#                         }
                        
#                         for workout in month_workouts:
#                             try:
#                                 workout_info = {
#                                     'date': workout.created_at.strftime('%Y-%m-%d'),
#                                     'name': workout.name,
#                                     'description': workout.description,
#                                     'completed': workout.completed,
#                                     'exercises': [
#                                         {
#                                             'name': exercise.name,
#                                             'weight': float(exercise.weight),
#                                             'repetitions': float(exercise.repetitions),
#                                             'target_muscle': exercise.get_target_muscle_display(),
#                                             'total_weight': float(exercise.total_weight)
#                                         }
#                                         for exercise in workout.exercise_set.all()
#                                     ]
#                                 }
#                                 monthly_data['workouts'].append(workout_info)
#                             except Exception as e:
#                                 logging.warning(f'Error processing workout {workout.id}: {str(e)}')
#                                 continue
                        
#                         training_data.append(monthly_data)
            
#             logging.info(f'Successfully retrieved training data for user {user.id}')
#             return training_data
            
#         except ObjectDoesNotExist:
#             logging.error(f'User {user.id} not found')
#             return []
#         except Exception as e:
#             logging.error(f'Error getting training data: {str(e)}')
#             return []

import logging
from datetime import datetime
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from ..models import Workout, Exercise

class ConversationService:
    def get_user_training_data(self, user):
        try:
            current_date = datetime.now()
            current_year = current_date.year
            current_month = current_date.month
            
            training_data = []
            
            # クエリの最適化のためにselect_relatedを使用
            with transaction.atomic():
                for i in range(6):
                    if current_month - i <= 0:
                        year = current_year - 1
                        month = 12 + (current_month - i)
                    else:
                        year = current_year
                        month = current_month - i
                        
                    start_date = datetime(year, month, 1)
                    if month == 12:
                        end_date = datetime(year + 1, 1, 1)
                    else:
                        end_date = datetime(year, month + 1, 1)
                    
                    month_workouts = (Workout.objects
                        .filter(
                            user=user,
                            created_at__gte=start_date,
                            created_at__lt=end_date
                        )
                        .select_related('user')
                        .prefetch_related('exercise_set')
                        .order_by('-created_at'))
                    
                    if month_workouts.exists():
                        monthly_data = {
                            'year_month': f'{year}年{month}月',
                            'workouts': []
                        }
                        
                        for workout in month_workouts:
                            try:
                                workout_info = {
                                    'date': workout.created_at.strftime('%Y-%m-%d'),
                                    'name': workout.name,
                                    'description': workout.description,
                                    'completed': workout.completed,
                                    'exercises': [
                                        {
                                            'name': exercise.name,
                                            'weight': float(exercise.weight),
                                            'repetitions': float(exercise.repetitions),
                                            'target_muscle': exercise.get_target_muscle_display(),
                                            'total_weight': float(exercise.total_weight)
                                        }
                                        for exercise in workout.exercise_set.all()
                                    ]
                                }
                                monthly_data['workouts'].append(workout_info)
                            except Exception as e:
                                logging.warning(f'Error processing workout {workout.id}: {str(e)}')
                                continue
                        
                        training_data.append(monthly_data)
            
            logging.info(f'Successfully retrieved training data for user {user.id}')
            return training_data
            
        except ObjectDoesNotExist:
            logging.error(f'User {user.id} not found')
            return []
        except Exception as e:
            logging.error(f'Error getting training data: {str(e)}')
            return []