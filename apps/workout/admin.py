from django.contrib import admin
from .models import (
    User, 
    Workout, 
    Exercise, 
    ProteinRecord,
    MuscleCount,
    MonthlyMuscleCount,
    ChatHistory,
    ChatMessage,
    ConversationLog
)

admin.site.register(User)
admin.site.register(Workout)
admin.site.register(Exercise)
admin.site.register(ProteinRecord)
admin.site.register(MuscleCount)
admin.site.register(MonthlyMuscleCount)
admin.site.register(ChatHistory)
admin.site.register(ChatMessage)
admin.site.register(ConversationLog)