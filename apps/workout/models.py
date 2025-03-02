from django.db import models
import re
from django.contrib.auth.hashers import make_password, check_password
from decimal import *
from datetime import date
from datetime import datetime

class UserManager(models.Manager):

    def register(self, **kwargs):
        errors = []


        ## USERNAME ##
        if len(kwargs["username"][0]) < 2:
            errors.append('ユーザー名は必須で、少なくとも2文字である必要があります。')

        USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9!@#$%^&*()?]*$')
        if not USERNAME_REGEX.match(kwargs["username"][0]):
            errors.append('ユーザー名は、文字、数字、基本的な文字のみを含む必要があります。')


        #4 EXISTING ##
        if len(User.objects.filter(username=kwargs["username"][0])) > 0:
            errors.append('ユーザー名はすでに他のユーザーに登録されています。')


        ## EMAIL ##
        # if len(kwargs["email"][0]) < 5:
        #     errors.append('メールアドレスは少なくとも5文字である必要があります。')

        # else:
        #     EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
        #     if not EMAIL_REGEX.match(kwargs["email"][0]):
        #         errors.append('メールアドレスの形式が正しくありません。')
        #     else:

        #         ## EXISTING ##
        #         if len(User.objects.filter(email=kwargs["email"][0])) > 0:
        #             errors.append('このメールアドレスはすでに他のユーザーに登録されています。')


        ## PASSWORD ##
        if len(kwargs["password"][0]) < 8 or len(kwargs["password_confirmation"][0]) < 8:
            errors.append('パスワードは必須で、少なくとも8文字である必要があります。')
        else:
            if kwargs["password"][0] != kwargs["password_confirmation"][0]:
                errors.append('パスワードと確認用パスワードが一致していません。')


        # TOS ACCEPT ##
        if kwargs["tos_accept"][0] == "on":
            kwargs["tos_accept"][0] = True
        else:
            errors.append("利用規約に同意する必要があります。")

        if len(errors) == 0:
            hashed_password = make_password(kwargs["password"][0])

            validated_user = {
                "logged_in_user": User(
                    username=kwargs["username"][0],
                    # email=kwargs["email"][0],
                    password=hashed_password,
                    tos_accept=kwargs["tos_accept"][0]
                ),
            }
            validated_user["logged_in_user"].save()
            return validated_user
        else:
            for error in errors:
                print("Validation Error: ", error)
            errors = {
                "errors": errors,
            }
            return errors


    def login(self, **kwargs):
        errors = []

        ## ALL FIELDS ##
        if len(kwargs["username"][0]) < 1 or len(kwargs["password"][0]) < 1:
            errors.append('すべてのフィールドは必須です。')
        else:

            ## EXISTING ##
            try:
                logged_in_user = User.objects.get(username=kwargs["username"][0])

                ## PASSWORD ##
                if not check_password(kwargs["password"][0], logged_in_user.password):
                    print("エラー: パスワードが正しくありません")
                    errors.append("ユーザー名またはパスワードが正しくありません。")

            except User.DoesNotExist:
                print("エラー: ユーザー名が無効です")
                errors.append('ユーザー名またはパスワードが正しくありません。')

        if len(errors) == 0:
            validated_user = {
                "logged_in_user": logged_in_user,
            }
            return validated_user
        else:
            for error in errors:
                print("Validation Error: ", error)
            errors = {
                "errors": errors,
            }
            return errors

class WorkoutManager(models.Manager):

    def new(self, **kwargs):
        errors = []

        ## NAME ##
        if len(kwargs["name"]) < 1:
            errors.append('名前は必須で、少なくとも1文字である必要があります。')

        WORKOUT_REGEX = re.compile(r'^\s*[\w\d\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF!@#$%^&*\"\':;\/?,<.>()-_=+\]\[~`]+(?:\s+[\w\d\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF!@#$%^&*\"\':;\/?,<.>()-_=+\]\[~`]+)*\s*$')

        if not WORKOUT_REGEX.match(kwargs["name"]):
            errors.append('名前は、文字、数字、基本的な文字のみを含む必要があります。')

        ## DESCRIPTION ##
        if len(kwargs["description"]) < 0:
            errors.append('説明は必須で、少なくとも2文字である必要があります。')

        # if not WORKOUT_REGEX.match(kwargs["description"]):
        #     errors.append('説明は、文字、数字、基本的な文字のみを含む必要があります。')

        if len(errors) == 0:
            validated_workout = {
                "workout": Workout(name=kwargs["name"], description=kwargs["description"], user=kwargs["user"]),
            }
            validated_workout["workout"].save()
            return validated_workout
        else:
            for error in errors:
                print("Validation Error: ", error)
            errors = {
                "errors": errors,
            }
            return errors

    def update(self, **kwargs):
        errors = []


        ## NAME ##
        if len(kwargs["name"]) < 1:
            errors.append('名前は必須で、少なくとも1文字である必要があります。')

        WORKOUT_REGEX = re.compile(r'^\s*[\w\d\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF!@#$%^&*\"\':;\/?,<.>()-_=+\]\[~`]+(?:\s+[\w\d\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF!@#$%^&*\"\':;\/?,<.>()-_=+\]\[~`]+)*\s*$')

        if not WORKOUT_REGEX.match(kwargs["name"]):
            errors.append('名前は、文字、数字、基本的な文字のみを含む必要があります。')

        ## DESCRIPTION ##
        if len(kwargs["description"]) < 0:
            errors.append('説明は必須で、少なくとも2文字である必要があります。')

        # if not WORKOUT_REGEX.match(kwargs["description"]):
        #     errors.append('説明は、文字、数字、基本的な文字のみを含む必要があります。')

        if len(errors) == 0:

            workout = Workout.objects.filter(id=kwargs['workout_id']).update(name=kwargs['name'], description=kwargs["description"])

            updated_workout = {
                "updated_workout": workout
            }
            return updated_workout
        else:
            for error in errors:
                print("Validation Error: ", error)
            errors = {
                "errors": errors,
            }
            return errors

class ExerciseManager(models.Manager):

    def new(self, **kwargs):
        errors = []


        ## REQUIRED ##
        if not kwargs['name'] or not kwargs['weight'] or not kwargs['repetitions']:
            errors.append('すべてのフィールドは必須です。')

        ## NAME ##
        if len(kwargs["name"]) < 1:
            errors.append('名前は必須で、少なくとも1文字である必要があります。')

        EXERCISE_REGEX = re.compile(r'^\s*[\w\d\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF!@#$%^&*\"\':;\/?,<.>()-_=+\]\[~`]+(?:\s+[\w\d\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF!@#$%^&*\"\':;\/?,<.>()-_=+\]\[~`]+)*\s*$')

        if not EXERCISE_REGEX.match(kwargs["name"]):
            errors.append('名前は、文字、数字、基本的な文字のみを含む必要があります。')


        ## WEIGHT & REPETITIONS ##
        try:
            kwargs["weight"] = round(float(kwargs["weight"]), 1)
            kwargs["repetitions"] = round(float(kwargs["repetitions"]), 1)

            if (kwargs["weight"] < 0) or (kwargs["repetitions"] < 0):
                errors.append('重さと繰り返しは正の数でなければなりません。')

        except ValueError:
            errors.append('重さと繰り返しは正の数で、小数点以下が最大である必要があります。')

        if len(errors) == 0:
            validated_exercise = {
                "exercise": Exercise(
                    name=kwargs["name"], 
                    weight=kwargs["weight"], 
                    repetitions=kwargs["repetitions"], 
                    workout=kwargs["workout"],
                    target_muscle=kwargs["target_muscle"]
                ),
            }
            validated_exercise["exercise"].save()
            return validated_exercise
        else:
            for error in errors:
                print("Validation Error: ", error)
            errors = {
                "errors": errors,
            }
            return errors

class User(models.Model):
    username = models.CharField(max_length=20)
    # email = models.CharField(max_length=50)
    password = models.CharField(max_length=22)
    tos_accept = models.BooleanField(default=False)
    level = models.IntegerField(default=1)
    level_name = models.CharField(max_length=15, default="Newbie")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

class Workout(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=150)
    completed = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = WorkoutManager()
    
    # 1/28
    @property
    def total(self):
        # 関連するExerciseオブジェクトの総和を計算
        total_weight = sum(exercise.total_weight for exercise in self.exercise_set.all())
        return total_weight

class Exercise(models.Model):
    name = models.CharField(max_length=50)
    weight = models.DecimalField(max_digits=999, decimal_places=1)
    repetitions = models.DecimalField(max_digits=999, decimal_places=1)
    category = models.CharField(max_length=50, default="Strength Training")
    target_muscle = models.CharField(max_length=20, choices=[
        ('soubou', '僧帽筋'),
        ('chest', '胸筋'),
        ('kouhaikin', '広背筋'),
        ('trapsmiddle', '背中中部'),
        ('shoulders', '肩'),
        ('biceps', '上腕二頭筋'),
        ('triceps', '上腕三頭筋'),
        ('zenwan', '前腕'),
        ('abs', '腹筋'),
        ('hukushakin', '腹斜筋'),
        ('quads', '大腿四頭筋'),
        ('hamstrings', 'ハムストリングス'),
        ('calves', 'ふくらはぎ'),
        ('lowerback', '腰部'),
        ('glutes', '臀筋')
    ])
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = ExerciseManager()
    
    @property
    def total_weight(self):
        return self.weight * self.repetitions
    
# 1/28
class ProteinRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    body_weight = models.DecimalField(max_digits=5, decimal_places=1)
    protein_intake = models.DecimalField(max_digits=5, decimal_places=1)
    judgment = models.CharField(max_length=1, choices=[('◎', '◎'), ('〇', '〇'), ('△', '△'), ('×', '×')])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

class MuscleCount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    muscle = models.CharField(max_length=20, choices=[
        ('soubou', '僧帽筋'),
        ('chest', '胸筋'),
        ('kouhaikin', '広背筋'),
        ('trapsmiddle', '背中中部'),
        ('shoulders', '肩'),
        ('biceps', '上腕二頭筋'),
        ('triceps', '上腕三頭筋'),
        ('zenwan', '前腕'),
        ('abs', '腹筋'),
        ('hukushakin', '腹斜筋'),
        ('quads', '大腿四頭筋'),
        ('hamstrings', 'ハムストリングス'),
        ('calves', 'ふくらはぎ'),
        ('lowerback', '腰部'),
        ('glutes', '臀筋')
    ])
    count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'muscle']
        
class MonthlyMuscleCount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    muscle = models.CharField(max_length=20, choices=[
        ('soubou', '僧帽筋'),
        ('chest', '胸筋'),
        ('kouhaikin', '広背筋'),
        ('trapsmiddle', '背中中部'),
        ('shoulders', '肩'),
        ('biceps', '上腕二頭筋'),
        ('triceps', '上腕三頭筋'),
        ('zenwan', '前腕'),
        ('abs', '腹筋'),
        ('hukushakin', '腹斜筋'),
        ('quads', '大腿四頭筋'),
        ('hamstrings', 'ハムストリングス'),
        ('calves', 'ふくらはぎ'),
        ('lowerback', '腰部'),
        ('glutes', '臀筋')
    ])
    count = models.IntegerField(default=0)
    year_month = models.DateField()  # 年月を保存
    
    class Meta:
        unique_together = ['user', 'muscle', 'year_month']
        
# models.pyに追加
class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
class ChatMessage(models.Model):
    chat_history = models.ForeignKey(ChatHistory, on_delete=models.CASCADE, related_name='messages')
    is_user = models.BooleanField(default=True)  # Trueならユーザーのメッセージ、FalseならAIのメッセージ
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
# models.pyに追加
class ConversationLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    conversation_type = models.CharField(max_length=20, default='recent')  # recent/important/summary
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at}"