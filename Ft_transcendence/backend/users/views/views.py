import logging
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from users.models import *
from matchmaking.models import MatchmakingQueue
from matchmaking.views.queue import queue_remote_add, queue_remote_remove
from games.models import Game
from games.views import *
from django.db.models import Q
from users.views.forms import *
from aouth.views.jwt import jwt_login_required

logger = logging.getLogger(__name__)

# Base views
# ----------

@jwt_login_required
def view_accueil(request):
    # logger.debug(f"ACCEUIL JWT tokens: {request.session.get('access_token')} {request.session.get('refresh_token')}")
    # logger.debug(f"ACCEUIL User ID: {request.user}")
    if request.is_ajax():
        html = render_to_string('spa_accueil.html', {'current_user': request.user, 'context': 'ajax'}, request=request)
        return JsonResponse({'html': html})
    else :
        return render(request, 'accueil.html', {'current_user': request.user})

@jwt_login_required
def view_perso(request):
    # logger.debug(f"PERSO JWT tokens: {request.session.get('access_token')} {request.session.get('refresh_token')}")
    # logger.debug(f"PERSO User ID: {request.user}")
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('spa_perso.html', {'current_user': request.user, 'context': 'ajax'}, request=request)
        return JsonResponse({'html': html})
    else:
        return render(request, 'perso.html', {'current_user': request.user, 'context': ''})


# Settings
# --------

@jwt_login_required
def view_setting(request):
    if request.user.password is not None:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string('spa_settings.html', {'current_user': request.user,'change_username_form': ChangeUsernameForm(instance=request.user),'change_image_form': ChangeImageForm(instance=request.user), 'change_2fa_form': Change2faForm(), 'change_password_form': ChangePasswordForm(), 'context': 'ajax'},request=request)
            return JsonResponse({'html': html})
        else:
            return render(request, 'settings.html', {
                'current_user': request.user,
                'change_username_form': ChangeUsernameForm(instance=request.user),
                'change_image_form': ChangeImageForm(instance=request.user),
                'change_2fa_form': Change2faForm(),
                'change_password_form': ChangePasswordForm()
            })
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string('spa_settings.html', {'current_user': request.user, 'change_username_form': ChangeUsernameForm(instance=request.user),'change_image_form': ChangeImageForm(instance=request.user), 'change_2fa_form': Change2faForm(),'context': ''}, request=request)
            return JsonResponse({'html': html})
        else:
            return render(request, 'settings.html', {
                'current_user': request.user,
                'change_username_form': ChangeUsernameForm(instance=request.user),
                'change_image_form': ChangeImageForm(instance=request.user),
                'change_2fa_form': Change2faForm()
            })

def update_user_stats(user):
    # Get all games that have not been processed yet
    if user.last_processed_game:
        unprocessed_games = Game.objects.filter(
            (Q(player1=user) | Q(player2=user)) & 
            Q(date_time__gt=user.last_processed_game.date_time)
            & Q(tournament__isnull=True)
        ).order_by('date_time')
    else:
        unprocessed_games = Game.objects.filter(
            (Q(player1=user) | Q(player2=user)) & Q(tournament__isnull=True)
        ).order_by('date_time')
    
    # Update user stats for each unprocessed game
    for game in unprocessed_games:
        if game.winner == user:
            user.wins += 1
            user.elo += 100
        elif game.draw == 0:
            user.losses += 1
            user.elo -= 100
        user.last_processed_game = game
    
    if unprocessed_games.exists():
        user.save()



@jwt_login_required
def view_profile(request):
    if request.user.status == "ingame":
        return redirect('home')
    user = request.user
    update_user_stats(user)
    matches = Game.objects.filter((Q(player1=user) | Q(player2=user)) & Q(tournament__isnull=True)).order_by('-date_time')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('spa_viewProfile.html', {'current_user': user, 'matches': matches, 'context': 'ajax'}, request=request)
        return JsonResponse({'html': html})
    else:
        return render(request, 'viewProfile.html', {'current_user': user, 'matches': matches, 'context': ''})
    
@jwt_login_required
def view_profile_friend(request, friend_user):
    if request.user.status == "ingame":
        return redirect('home')
    user_profile = get_object_or_404(User, username=friend_user)
    friends_user = request.user.friends.all()
    
    for friends_user in friends_user:
       if friends_user.username == friend_user:
           break
    user = request.user
    update_user_stats(friends_user)
    matches = Game.objects.filter((Q(player1=friends_user) | Q(player2=friends_user)) & Q(tournament__isnull=True)).order_by('-date_time')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('spa_viewProfile.html', {'current_user': user_profile, 'matches': matches, 'context': 'ajax'}, request=request)
        return JsonResponse({'html': html})
    else:
        return render(request, 'viewProfile.html', {'current_user': user_profile, 'matches': matches, 'context': ''})
    
@jwt_login_required
def redirect_user(request):
    current_game = request.user.current_game
    if request.user.status == 'ingame':
        score1 = current_game.player1_score
        score2 = current_game.player2_score
        logger.info("match in progress")
        # if current_game.player1 == request.user:
        score1 = 0
        score2 = 0
        game_update(request, current_game, score1, score2)
    return JsonResponse({'redirect': 'home', 'message': 'success'})