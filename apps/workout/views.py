from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Workout, Exercise, ProteinRecord, MuscleCount, MonthlyMuscleCount
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from datetime import date
import json
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from openai import AzureOpenAI
from .services.conversation_service import ConversationService
import logging
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
from django.db import transaction
from django.core.cache import cache
from django.db.models import Count
from django.db.models.functions import TruncMonth
from .models import ChatHistory, ChatMessage

def login(request):
    if request.method == "GET":
        return render(request, "workout/index.html")

    if request.method == "POST":
        validated = User.objects.login(**request.POST)
        try:
            if len(validated["errors"]) > 0:
                print("ユーザーはログインできませんでした。")
                for error in validated["errors"]:
                    messages.error(request, error, extra_tags='login')
                return redirect("/")
        except KeyError:
            print("ユーザーが検証を通過し、ログインしています。")
            
            user = validated["logged_in_user"]
            request.session["user_id"] = user.id
            
            # ログイン時の日付をチェック
            current_date = datetime.now()
            print(f"ログイン時の日付: {current_date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 最終アクセス日をチェック
            last_access = cache.get(f'last_access_{user.id}')
            if last_access:
                print(f"前回のアクセス日: {last_access}")
                last_date = datetime.strptime(last_access, '%Y-%m-%d')
                
                # 年と月を比較
                current_ym = current_date.strftime('%Y-%m')
                last_ym = last_date.strftime('%Y-%m')
                
                if current_ym > last_ym:  # 年月が進んでいる場合のみ更新
                    print(f"月次更新が必要: {last_ym} → {current_ym}")
                    try:
                        with transaction.atomic():
                            current_counts = MuscleCount.objects.filter(user=user)
                            
                            # 前月のデータを保存
                            for count in current_counts:
                                MonthlyMuscleCount.objects.create(
                                    user=user,
                                    muscle=count.muscle,
                                    count=count.count,
                                    year_month=last_date.replace(day=1)
                                )
                            
                            # カウントをリセット
                            current_counts.update(count=0)
                            print("月次更新が完了しました")
                    except Exception as e:
                        print(f"月次更新中にエラーが発生: {str(e)}")
                else:
                    print(f"月次更新は不要です（同じ月内: {current_ym}）")
            else:
                print("前回のアクセス記録なし")
            
            # 最終アクセス日を更新
            cache.set(f'last_access_{user.id}', current_date.strftime('%Y-%m-%d'), timeout=None)

            return redirect("/dashboard")

def register(request):

    if request.method == "GET":
        return render(request, "workout/register.html")

    if request.method == "POST":
        validated = User.objects.register(**request.POST)
        try:
            if len(validated["errors"]) > 0:
                print("ユーザーは登録できませんでした。")
                for error in validated["errors"]:
                    messages.error(request, error, extra_tags='registration')
                return redirect("/user/register")
        except KeyError:
            print("ユーザーが検証を通過し、作成されました。")
            request.session["user_id"] = validated["logged_in_user"].id
            return redirect('/dashboard')

def logout(request):
    try:
        user_id = request.session["user_id"]
        # ログアウト時の日付を記録
        current_date = datetime.now()
        print(f"ログアウト時の日付: {current_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"ユーザーID {user_id} の最終アクセス日を更新")
        
        # 最終アクセス日を更新
        cache.set(f'last_access_{user_id}', current_date.strftime('%Y-%m-%d'), timeout=None)
        
        del request.session['user_id']
        messages.success(request, "ログアウトしました。", extra_tags='logout')

    except KeyError:
        pass

    return redirect("/")

def dashboard(request):

    try:
        user = User.objects.get(id=request.session["user_id"])

        recent_workouts = Workout.objects.filter(user__id=user.id).order_by('-id')[:4]

        data = {
            'user': user,
            'recent_workouts': recent_workouts,
        }

        return render(request, "workout/dashboard.html", data)

    except (KeyError, User.DoesNotExist) as err:
        messages.info(request, "このページを表示するにはログインする必要があります。", extra_tags="invalid_session")
        return redirect("/")

def new_workout(request):

    try:
        user = User.objects.get(id=request.session["user_id"])

        data = {
            'user': user,
        }

        if request.method == "GET":
            return render(request, "workout/add_workout.html", data)

        if request.method == "POST":
            workout = {
                "name": request.POST["name"],
                "description": request.POST["description"],
                "user": user
            }

            validated = Workout.objects.new(**workout)

            try:
                if len(validated["errors"]) > 0:
                    print("ワークアウトを作成できませんでした。")
                    for error in validated["errors"]:
                        messages.error(request, error, extra_tags='workout')
                    return redirect("/workout")
            except KeyError:
                print("ワークアウトが検証を通過し、作成されました。")

                id = str(validated['workout'].id)
                return redirect('/workout/' + str(id))

    except (KeyError, User.DoesNotExist) as err:
        messages.info(request, "このページを表示するにはログインする必要があります。", extra_tags="invalid_session")
        return redirect("/")

def workout(request, id):

    try:
        user = User.objects.get(id=request.session["user_id"])

        data = {
            'user': user,
            'workout': Workout.objects.get(id=id),
            'exercises': Exercise.objects.filter(workout__id=id).order_by('-updated_at'),
        }

        return render(request, "workout/workout.html", data)

    except (KeyError, User.DoesNotExist) as err:
        messages.info(request, "このページを表示するにはログインする必要があります。", extra_tags="invalid_session")
        return redirect("/")

def all_workouts(request):

    try:
        user = User.objects.get(id=request.session["user_id"])

        workout_list = Workout.objects.filter(user__id=user.id).order_by('-id')

        page = request.GET.get('page', 1)

        paginator = Paginator(workout_list, 12)
        try:
            workouts = paginator.page(page)
        except PageNotAnInteger:
            workouts = paginator.page(1)
        except EmptyPage:
            workouts = paginator.page(paginator.num_pages)

        data = {
            'user': user,
            'workouts': workouts,
        }

        return render(request, "workout/all_workouts.html", data)

    except (KeyError, User.DoesNotExist) as err:
        messages.info(request, "このページを表示するにはログインする必要があります。", extra_tags="invalid_session")
        return redirect("/")

def exercise(request, id):
    try:
        user = User.objects.get(id=request.session["user_id"])

        if request.method == "POST":
            exercise = {
                "name": request.POST["name"],
                "weight": request.POST["weight"],
                "repetitions": request.POST["repetitions"],
                "target_muscle": request.POST["target_muscle"],
                "workout": Workout.objects.get(id=id),
            }

            validated = Exercise.objects.new(**exercise)

            try:
                if len(validated["errors"]) > 0:
                    print("エクササイズを作成できませんでした。")
                    for error in validated["errors"]:
                        messages.error(request, error, extra_tags='exercise')
                    return redirect("/workout/" + str(id))
            except KeyError:
                print("エクササイズが検証を通過し、作成されました。")
                
                # 全ての部位に対応
                target_muscle = exercise["target_muscle"]
                muscle_count, created = MuscleCount.objects.get_or_create(
                    user=user,
                    muscle=target_muscle,
                    defaults={'count': 0}
                )
                muscle_count.count += 1
                muscle_count.save()

                return redirect('/workout/' + str(id))

    except (KeyError, User.DoesNotExist) as err:
        messages.info(request, "このページを表示するにはログインする必要があります。", extra_tags="invalid_session")
        return redirect("/")

def edit_workout(request, id):

    try:
        user = User.objects.get(id=request.session["user_id"])

        data = {
            'user': user,
            'workout': Workout.objects.get(id=id),
            'exercises': Exercise.objects.filter(workout__id=id),
        }

        if request.method == "GET":
            return render(request, "workout/edit_workout.html", data)

        if request.method == "POST":
            workout = {
                'name': request.POST['name'],
                'description': request.POST['description'],
                'workout_id': data['workout'].id,
            }

            validated = Workout.objects.update(**workout)

            try:
                if len(validated["errors"]) > 0:
                    print("ワークアウトを編集できませんでした。")
                    for error in validated["errors"]:
                        messages.error(request, error, extra_tags='edit')
                    return redirect("/workout/" + str(data['workout'].id) + "/edit")
            except KeyError:
                print("編集されたワークアウトが検証を通過し、更新されました。")

                return redirect("/workout/" + str(data['workout'].id))

    except (KeyError, User.DoesNotExist) as err:
        messages.info(request, "このページを表示するにはログインする必要があります。", extra_tags="invalid_session")
        return redirect("/")

def delete_workout(request, id):
    try:
        user = User.objects.get(id=request.session["user_id"])
        
        # 削除するワークアウトに関連する全てのエクササイズを取得
        workout = Workout.objects.get(id=id)
        exercises = Exercise.objects.filter(workout=workout)
        
        # 各エクササイズの部位のカウントを減らす
        with transaction.atomic():  # トランザクションで一括処理
            for exercise in exercises:
                try:
                    muscle_count = MuscleCount.objects.get(
                        user=user,
                        muscle=exercise.target_muscle
                    )
                    # カウントを1減らす（0未満にはならないようにする）
                    muscle_count.count = max(0, muscle_count.count - 1)
                    muscle_count.save()
                except MuscleCount.DoesNotExist:
                    # 万が一の場合の対応
                    pass
            
            # ワークアウトを削除
            workout.delete()

        return redirect('/dashboard')

    except (KeyError, User.DoesNotExist) as err:
        messages.info(request, "このページを表示するにはログインする必要があります。", extra_tags="invalid_session")
        return redirect("/")

def complete_workout(request, id):

    try:
        user = User.objects.get(id=request.session["user_id"])

        if request.method == "GET":
            return redirect("/workout/" + str(id))

        if request.method == "POST":

            workout = Workout.objects.get(id=id)
            workout.completed = True
            workout.save()

            print("ワークアウトが完了しました。")

            return redirect('/workout/' + str(id))

    except (KeyError, User.DoesNotExist) as err:
        messages.info(request, "このページを表示するにはログインする必要があります。", extra_tags="invalid_session")
        return redirect("/")

def tos(request):

    return render(request, "workout/legal/tos.html")

def prelusion(request):
    return render(request, 'workout/prelusion.html')

# def calc(request):
#     return render(request, 'workout/calc.html')

def duplicateExercise(request, exercise_id, workout_id):
    try:
        original_exercise = Exercise.objects.get(id=exercise_id)

        duplicated_exercise = Exercise.objects.create(
            name=original_exercise.name,
            weight=original_exercise.weight,
            repetitions=original_exercise.repetitions,
            category=original_exercise.category,
            workout_id=workout_id
        )

        response_data = {
            'success': True,
            'message': 'エクササイズが複製されました。',
            'duplicated_exercise_id': duplicated_exercise.id,
        }

    except Exercise.DoesNotExist:
        response_data = {
            'success': False,
            'message': '指定されたエクササイズが見つかりません。',
        }

    return JsonResponse(response_data)

def calc(request):
    if request.method == "POST":
        try:
            user = User.objects.get(id=request.session["user_id"])
            body_weight = float(request.POST["body_weight"])
            protein_intake = float(request.POST["protein_intake"])

            required_protein = round(body_weight * 1.4, 1)

            if protein_intake >= body_weight * 2:
                judgment = '◎'
            elif protein_intake >= body_weight * 1.4:
                judgment = '〇'
            elif protein_intake >= body_weight * 1.0:
                judgment = '△'
            else:
                judgment = '×'

            ProteinRecord.objects.create(user=user, date=date.today(), body_weight=body_weight, protein_intake=protein_intake, judgment=judgment)

            messages.success(request, "摂取記録が保存されました。", extra_tags='calculation')

            protein_records = ProteinRecord.objects.filter(user=user).order_by('-date', '-created_at')[:7]
            calculation_data = {
                'body_weight': body_weight,
                'protein_intake': protein_intake,
                'required_protein': required_protein,
                'judgment': judgment,
            }

            return render(request, 'workout/calc.html', {'protein_records': protein_records, 'calculation_data': calculation_data})

        except (KeyError, User.DoesNotExist, ValueError):
            # エラーメッセージ
            messages.error(request, "摂取記録の保存に失敗しました。", extra_tags='calculation')

    user = User.objects.get(id=request.session["user_id"])
    protein_records = ProteinRecord.objects.filter(user=user).order_by('-date', '-created_at')[:7]
    return render(request, 'workout/calc.html', {'protein_records': protein_records})

def chat(request):
    return render(request, 'workout/chat.html')

endpoint = "https://xxx.azure.com/"
api_key = "XXX"
deployment = "gpt-4o"


client = AzureOpenAI(
    api_key=api_key,
    # api_version="2024-02-01",
    api_version = "2024-02-15-preview",
    azure_endpoint=endpoint
)

@csrf_exempt
def chat_response(request):
    if request.method == 'POST':
        try:
            user = User.objects.get(id=request.session["user_id"])
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            # 会話サービスを初期化
            conv_service = ConversationService()
            
            # トレーニングデータを取得
            training_data = conv_service.get_user_training_data(user)
            
            if not training_data:
                logging.warning(f'No training data found for user {user.id}')
                training_data_message = "トレーニング履歴がまだありません。"
            else:
                training_data_message = json.dumps(training_data, ensure_ascii=False, indent=2)
            
            # 現在のチャット履歴を取得または新規作成
            current_chat = ChatHistory.objects.filter(user=user).order_by('-created_at').first()
            if not current_chat:
                current_chat = ChatHistory.objects.create(
                    user=user,
                    title=datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                )
            
            recent_messages = ChatMessage.objects.filter(
                chat_history=current_chat
            ).order_by('-created_at')[:10]

            conversation_history = "\n".join([
                f"{'User' if msg.is_user else 'Assistant'}: {msg.content}"
                for msg in reversed(recent_messages)  # 古いメッセージから順に表示
            ])
            
            # ユーザーメッセージを保存
            ChatMessage.objects.create(
                chat_history=current_chat,
                is_user=True,
                content=user_message
            )
            
            def event_stream():
                try:
                    # トレーニングデータの月数をカウント
                    num_months = len(training_data)
                    
                    if num_months <= 1:
                        # 1ヶ月目用のプロンプト
                        system_prompt = f"""You are an expert AI assistant specializing in workout and fitness advice.

User's current training data:
{training_data_message}

Recent conversation history:
{conversation_history}

This user has just started recording their training data this month. Please:

Very important formatting rules (please follow exactly):
1. Use Japanese language with polite style (です/ます)
2. End complete sentences with 。(Japanese period)
3. Add a line break after each sentence ending with 。
4. For bullet points:
   - ONLY use "- " (hyphen + space)
   - NEVER use "*" or "・" or any other symbols
   - Each bullet point must be a complete sentence
   - Add empty lines before and after bullet point groups

Example format:
これは最初の段落です。

以下の点について分析しました。

- 一つ目のポイントはこのように書きます。
- 二つ目のポイントもハイフンで始めます。
- 三つ目のポイントも同じ形式で書きます。

これは次の段落です。

Analysis requirements:
1. Focus on analyzing their current training patterns:
   - Compare workouts from different days
   - Check for patterns in muscle groups being trained
   - Analyze weight and rep progressions within the month
   - Note their exercise preferences

2. Provide specific observations:
   - Mention actual weights and reps they're using
   - Point out which muscle groups they're focusing on
   - Highlight any progression you notice

3. Offer encouragement and next steps:
   - Acknowledge their commitment to tracking workouts
   - Suggest reasonable progressions based on current performance
   - Recommend complementary exercises for balance

Please follow this format exactly, especially using ONLY "- " for bullet points."""

                    else:
                        # 2ヶ月目以降の既存のプロンプト
                        system_prompt = f"""You are an expert AI assistant specializing in workout and fitness advice.

User's training history (past 6 months):
{training_data_message}

Recent conversation history:
{conversation_history}

Very important formatting rules (please follow exactly):
1. Use Japanese language with polite style (です/ます)
2. End complete sentences with 。(Japanese period)
3. Add a line break after each sentence ending with 。
4. For bullet points:
   - ONLY use "- " (hyphen + space)
   - NEVER use "*" or "・" or any other symbols
   - Each bullet point must be a complete sentence
   - Add empty lines before and after bullet point groups

Analysis points:
- Compare monthly progress
- Identify training patterns
- Suggest improvements
- Provide encouragement

Example format:
これは最初の段落です。

以下の点について分析しました。

- 一つ目のポイントはこのように書きます。
- 二つ目のポイントもハイフンで始めます。
- 三つ目のポイントも同じ形式で書きます。

これは次の段落です。

Please analyze the user's training data by month and:
1. Track their progress over time
2. Identify trends in their training patterns
3. Compare current month's performance with previous months
4. Suggest improvements based on their historical data

Please follow this format exactly, especially using ONLY "- " for bullet points."""
                    
                    completion = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message}
                        ],
                        stream=True
                    )
                    
                    full_response = ""
                    for chunk in completion:
                        if chunk.choices and len(chunk.choices) > 0:
                            if chunk.choices[0].delta.content is not None:
                                content = chunk.choices[0].delta.content
                                full_response += content
                                yield f"data: {content}\n\n"
                    
                    # AIの応答を保存
                    ChatMessage.objects.create(
                        chat_history=current_chat,
                        is_user=False,
                        content=full_response
                    )
                    
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    logging.error(f'Error in event_stream: {str(e)}')
                    print(f"An error occurred: {str(e)}")
                    yield f"data: Error: {str(e)}\n\n"
                    yield "data: [DONE]\n\n"
            
            return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        except Exception as e:
            logging.error(f'Error in chat_response: {str(e)}')
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)
    
def get_muscle_counts(request):
    """筋肉部位ごとのカウントを取得するAPI"""
    try:
        user = User.objects.get(id=request.session["user_id"])
        muscle_counts = MuscleCount.objects.filter(user=user)
        data = {count.muscle: count.count for count in muscle_counts}
        return JsonResponse(data)
    except (KeyError, User.DoesNotExist):
        return JsonResponse({}, status=401)
    
def model(request):
    """モデル表示ページ"""
    try:
        user = User.objects.get(id=request.session["user_id"])
        muscle_counts = MuscleCount.objects.filter(user=user)
        counts = {count.muscle: count.count for count in muscle_counts}
        
        return render(request, 'workout/model.html', {
            'user': user,
            'muscle_counts': counts
        })
    except (KeyError, User.DoesNotExist) as err:
        messages.info(request, "このページを表示するにはログインする必要があります。", extra_tags="invalid_session")
        return redirect("/")

def history(request):
    try:
        user = User.objects.get(id=request.session["user_id"])
        
        # 月次データの取得
        monthly_data = MonthlyMuscleCount.objects.filter(user=user)\
            .values('year_month')\
            .distinct()\
            .order_by('-year_month')
            
        data = {
            'user': user,
            'monthly_data': monthly_data,
        }
        
        return render(request, 'workout/history.html', data)
        
    except (KeyError, User.DoesNotExist) as err:
        messages.info(request, "このページを表示するにはログインする必要があります。", extra_tags="invalid_session")
        return redirect("/")

def get_monthly_muscle_counts(request, year, month):
    """特定の月の筋肉部位ごとのカウントを取得するAPI"""
    try:
        user = User.objects.get(id=request.session["user_id"])
        target_date = datetime(year=int(year), month=int(month), day=1)
        
        muscle_counts = MonthlyMuscleCount.objects.filter(
            user=user,
            year_month=target_date
        )
        
        data = {count.muscle: count.count for count in muscle_counts}
        return JsonResponse(data)
        
    except (KeyError, User.DoesNotExist):
        return JsonResponse({}, status=401)

# views.py のadvance_month関数を修正
@require_POST
@csrf_exempt
def advance_month(request):
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.session["user_id"])
            
            # キャッシュから現在の仮想日付を取得（なければ現在の日付）
            current_virtual_date = cache.get(f'virtual_date_{user.id}')
            if not current_virtual_date:
                current_virtual_date = datetime.now().replace(day=1)
                
            # 現在の月のデータを保存（current_virtual_dateを使用）
            current_counts = MuscleCount.objects.filter(user=user)
            
            # 現在の月のデータを保存
            for count in current_counts:
                MonthlyMuscleCount.objects.create(
                    user=user,
                    muscle=count.muscle,
                    count=count.count,
                    year_month=current_virtual_date  # 現在の月のデータを保存
                )
            
            # カウントをリセット
            current_counts.update(count=0)
            
            # 次の月を計算して保存
            if current_virtual_date.month == 12:
                next_virtual_date = current_virtual_date.replace(year=current_virtual_date.year + 1, month=1)
            else:
                next_virtual_date = current_virtual_date.replace(month=current_virtual_date.month + 1)
            
            # 新しい仮想日付をキャッシュに保存
            cache.set(f'virtual_date_{user.id}', next_virtual_date, timeout=None)
            
            print(f"データを保存した月: {current_virtual_date.strftime('%Y/%m/%d')}")
            print(f"次の月: {next_virtual_date.strftime('%Y/%m/%d')}")
        
        return JsonResponse({
            'success': True, 
            'next_date': next_virtual_date.strftime('%Y/%m/%d')
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
@csrf_exempt
def save_chat_history(request):
    if request.method == 'POST':
        try:
            user = User.objects.get(id=request.session["user_id"])
            data = json.loads(request.body)
            messages = data.get('messages', [])
            
            # タイトルを現在の日時で生成
            base_title = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            title = base_title
            counter = 1
            
            # タイトルが重複する場合は (X) を付加
            while ChatHistory.objects.filter(user=user, title=title).exists():
                title = f"{base_title} ({counter})"
                counter += 1
            
            # チャット履歴を作成
            chat_history = ChatHistory.objects.create(
                user=user,
                title=title
            )
            
            # メッセージを保存
            for msg in messages:
                ChatMessage.objects.create(
                    chat_history=chat_history,
                    is_user=msg['is_user'],
                    content=msg['content']
                )
            
            return JsonResponse({'success': True, 'history_id': chat_history.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def get_chat_histories(request):
    try:
        user = User.objects.get(id=request.session["user_id"])
        histories = ChatHistory.objects.filter(user=user).order_by('-created_at')
        data = [{
            'id': h.id,
            'title': h.title,
            'created_at': h.created_at.strftime('%Y/%m/%d %H:%M:%S')
        } for h in histories]
        return JsonResponse({'success': True, 'histories': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def get_chat_messages(request, history_id):
    try:
        user = User.objects.get(id=request.session["user_id"])
        history = ChatHistory.objects.get(id=history_id, user=user)
        messages = ChatMessage.objects.filter(chat_history=history).order_by('created_at')
        data = [{
            'is_user': msg.is_user,
            'content': msg.content,
            'created_at': msg.created_at.strftime('%Y/%m/%d %H:%M:%S')
        } for msg in messages]
        return JsonResponse({'success': True, 'messages': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def delete_chat_history(request, history_id):
    if request.method == 'POST':
        try:
            user = User.objects.get(id=request.session["user_id"])
            history = ChatHistory.objects.get(id=history_id, user=user)
            history.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def delete_exercise(request, workout_id, exercise_id):
    try:
        exercise = Exercise.objects.get(id=exercise_id)
        exercise.delete()
        return redirect(f'/workout/{workout_id}')
    except Exercise.DoesNotExist:
        messages.error(request, "エクササイズが見つかりませんでした。", extra_tags='exercise')
        return redirect(f'/workout/{workout_id}')