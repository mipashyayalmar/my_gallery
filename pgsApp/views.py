from django.shortcuts import redirect, render,get_object_or_404
import json
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from pgsApp import models, forms
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from .models import Gallery, UserInteraction
from .forms import SaveUpload 


def context_data():
    context = {
        'page_name' : '',
        'page_title' : '',
        'system_name' : 'Reflections of Childhood ',
        'topbar' : True,
        'footer' : True,
    }

    return context
    
def userregister(request):
    context = context_data()
    context['topbar'] = False
    context['footer'] = False
    context['page_title'] = "User Registration"
    if request.user.is_authenticated:
        return redirect("home-page")
    return render(request, 'register.html', context)


@login_required
def upload_modal(request):
    if request.method == 'POST':
        form = SaveUpload(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'failed', 'msg': form.errors.as_json()})
    else:
        form = SaveUpload()
        context = {
            'form': form,
            'user': request.user
        }
    return render(request, 'upload.html', context)

def save_register(request):
    resp={'status':'failed', 'msg':''}
    if not request.method == 'POST':
        resp['msg'] = "No data has been sent on this request"
    else:
        form = forms.SaveUser(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your Account has been created succesfully")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if resp['msg'] != '':
                        resp['msg'] += str('<br />')
                    resp['msg'] += str(f"[{field.name}] {error}.")
            
    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def update_profile(request):
    context = context_data()
    context['page_title'] = 'Update Profile'
    user = User.objects.get(id = request.user.id)
    if not request.method == 'POST':
        form = forms.UpdateProfile(instance=user)
        context['form'] = form
        print(form)
    else:
        form = forms.UpdateProfile(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile has been updated")
            return redirect("profile-page")
        else:
            context['form'] = form
            
    return render(request, 'manage_profile.html',context)


@login_required
def update_password(request):
    context =context_data()
    context['page_title'] = "Update Password"
    if request.method == 'POST':
        form = forms.UpdatePasswords(user = request.user, data= request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Your Account Password has been updated successfully")
            update_session_auth_hash(request, form.user)
            return redirect("profile-page")
        else:
            context['form'] = form
    else:
        form = forms.UpdatePasswords(request.POST)
        context['form'] = form
    return render(request,'update_password.html',context)


# Create your views here.
def login_page(request):
    context = context_data()
    context['topbar'] = False
    context['footer'] = False
    context['page_name'] = 'login'
    context['page_title'] = 'Login'
    return render(request, 'login.html', context)

def login_user(request):
    logout(request)
    resp = {"status":'failed','msg':''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status']='success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp),content_type='application/json')

# Inside your views.py file

@login_required
def home(request):
    context = context_data()
    context['page'] = 'home'
    context['page_title'] = 'Home'
    
    # Total posts and users
    context['total_posts'] = models.Gallery.objects.filter(delete_flag=0).count()
    context['total_users'] = User.objects.count()
    
    # Personal post and trash counts for the logged-in user
    context['personal_posts'] = models.Gallery.objects.filter(delete_flag=0, user=request.user).count()
    context['personal_trash'] = models.Gallery.objects.filter(delete_flag=1, user=request.user).count()
    
    return render(request, 'home.html', context)

def logout_user(request):
    logout(request)
    return redirect('login-page')
    
@login_required
def profile(request):
    context = context_data()
    context['page'] = 'profile'
    context['page_title'] = "Profile"
    return render(request,'profile.html', context)

@login_required
def save_upload(request):
    resp = {'status': 'failed', 'msg': ''}
    if not request.method == 'POST':
        resp['msg'] = "No data has been sent on this request"
    else:
        form = forms.SaveUpload(request.POST, request.FILES)
        if form.is_valid():
            # Save the uploaded image
            uploaded_image = form.save()
            messages.success(request, "New Upload has been saved successfully.")

            # Create a notification for all users
            create_notification(Notification.ALL_USERS, request.user, f"{request.user.username} has uploaded a new image: {uploaded_image.caption}.")

            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if resp['msg'] != '':
                        resp['msg'] += str('<br />')
                    resp['msg'] += str(f"[{field.name}] {error}.")
    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def view_gallery(request):
    context = context_data()
    context['page_title'] ="Gallery"
    context['photos'] = models.Gallery.objects.filter(user = request.user, delete_flag = 0).all()
    return render(request, 'gallery.html', context) 

@login_required
def view_trash(request):
    context = context_data()
    context['page_title'] ="Trashed Images"
    context['photos'] = models.Gallery.objects.filter(user = request.user, delete_flag = 1).all()
    return render(request, 'trash.html', context) 

@login_required
def trash_upload(request, pk =None):
    resp = {'status':'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'No data sent in this request'
    else:
        try:
            upload = models.Gallery.objects.filter(id=pk).update(delete_flag = 1)
            resp['status'] = 'success'
            messages.success(request, 'Image has been moved to trash successfully')
        except:
            resp['msg'] = 'Invalid data to delete'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def restore_upload(request, pk =None):
    resp = {'status':'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'No data sent in this request'
    else:
        try:
            upload = models.Gallery.objects.filter(id=pk).update(delete_flag = 0)
            resp['status'] = 'success'
            messages.success(request, 'Image has been restore successfully')
        except:
            resp['msg'] = 'Invalid data to delete'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def delete_upload(request, pk =None):
    resp = {'status':'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'No data sent in this request'
    else:
        try:
            upload = models.Gallery.objects.get(id=pk).delete()
            resp['status'] = 'success'
            messages.success(request, 'Image has been deleted forever successfully')
        except:
            resp['msg'] = 'Invalid data to delete'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def all_uploads(request):
    # Get base context with top and bottom bars
    context = context_data()
    context['page'] = 'all_uploads'  # For active menu highlighting
    context['page_title'] = "All Uploads"
    
    # Search functionality
    search_query = request.GET.get('search', '')
    filters = Q(delete_flag=False)  # Only non-deleted images
    
    if search_query:
        filters &= Q(caption__icontains=search_query) | Q(user__username__icontains=search_query)
        context['search_query'] = search_query  # Add search query to context for form persistence
    
    # Pagination setup
    page = request.GET.get('page', 1)
    items_per_page = 12  # You can adjust this number
    
    # Get all photos matching the filters
    photos = Gallery.objects.filter(filters).order_by('-date_created')
    
    # Add additional context data
    context.update({
        'photos': photos,
        'total_photos': photos.count(),
        'topbar': True,  # Enable top bar
        'footer': True,  # Enable bottom bar
        'enable_search': True,  # Enable search functionality
        'current_time': timezone.now(),  # Add current time for display
    })
    
    # You might want to add some statistics
    if request.user.is_authenticated:
        context.update({
            'user_uploads': Gallery.objects.filter(user=request.user, delete_flag=False).count(),
            'total_likes': sum(photo.likes for photo in photos),
            'total_interactions': UserInteraction.objects.filter(image__in=photos).count(),
        })
    
    return render(request, 'all_uploads.html', context)
    

@login_required
def all_users(request):
    context = context_data()
    context['page_title'] = "All Users"
    context['users'] = User.objects.all()  # Get all users
    return render(request, 'all_users.html', context)
# pgsApp/views.py

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import transaction
import json
from .models import Gallery, UserInteraction,Notification
from .utils import create_notification  # Import the notification function

@login_required
def toggle_image_interaction(request, image_id):
    image = get_object_or_404(Gallery, id=image_id)

    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')

        with transaction.atomic():
            interaction = UserInteraction.objects.filter(user=request.user, image=image).first()

            # Prepare default response
            response_data = {
                'likes': image.likes,
                'dislikes': image.dislikes,
                'status': ''
            }

            if action == 'like':
                if interaction:
                    if interaction.interaction_type == 'like':
                        image.likes -= 1
                        interaction.delete()
                        response_data['status'] = 'unliked'
                    else:
                        image.dislikes -= 1
                        interaction.interaction_type = 'like'
                        interaction.save()
                        image.likes += 1
                        response_data['status'] = 'liked'
                else:
                    UserInteraction.objects.create(user=request.user, image=image, interaction_type='like')
                    image.likes += 1
                    response_data['status'] = 'liked'
                
                image.save()
                response_data['likes'] = image.likes
                response_data['dislikes'] = image.dislikes

            elif action == 'dislike':
                if interaction:
                    if interaction.interaction_type == 'dislike':
                        image.dislikes -= 1
                        interaction.delete()
                        response_data['status'] = 'undisliked'
                    else:
                        image.likes -= 1
                        interaction.interaction_type = 'dislike'
                        interaction.save()
                        image.dislikes += 1
                        response_data['status'] = 'disliked'
                else:
                    UserInteraction.objects.create(user=request.user, image=image, interaction_type='dislike')
                    image.dislikes += 1
                    response_data['status'] = 'disliked'

                image.save()
                response_data['likes'] = image.likes
                response_data['dislikes'] = image.dislikes

            # Determine if user currently likes or dislikes the image
            user_interaction = UserInteraction.objects.filter(user=request.user, image=image).first()
            if user_interaction:
                response_data['user_interaction'] = user_interaction.interaction_type
            else:
                response_data['user_interaction'] = None  # No interaction

            return JsonResponse(response_data)

    return JsonResponse({'status': 'error', 'message': 'Invalid action'})


from .models import UserNotification
@login_required
def notifications_view(request):
    context = context_data()  # Include the base context data
    context['page_title'] = "Notifications"
    
    # Fetch notifications for all users, filtering out any that the user has deleted.
    all_notifications = Notification.objects.filter(notification_type=Notification.ALL_USERS)
    user_notifications = Notification.objects.filter(notification_type=Notification.SPECIFIC_USER, user=request.user)
    
    # Exclude notifications that have been deleted by this user
    deleted_notifications = UserNotification.objects.filter(user=request.user, deleted=True).values_list('notification_id', flat=True)
    combined_notifications = (all_notifications | user_notifications).exclude(id__in=deleted_notifications).distinct().order_by('-created_at')
    
    context['notifications'] = combined_notifications
    return render(request, 'notifications.html', context)



@login_required
def delete_notification(request, notification_id):
    if request.method == 'POST':
        resp = {'status': 'failed', 'message': 'Notification not found.'}
        try:
            # Check if the notification exists
            notification = Notification.objects.get(id=notification_id)
            # Get or create a UserNotification record to mark it as deleted
            user_notification, created = UserNotification.objects.get_or_create(user=request.user, notification=notification)
            user_notification.deleted = True
            user_notification.save()
            resp['status'] = 'success'
        except Notification.DoesNotExist:
            resp['message'] = 'Notification does not exist or cannot be deleted.'
        return JsonResponse(resp)
    else:
        return JsonResponse({'status': 'failed', 'message': 'Invalid request method.'})


def some_view(request):
    # Fetch count of unread notifications or any specific logic for counting
    notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
    context = {
        'notifications_count': notifications_count,
        'page_title': 'Your Page Title',  # Add other context variables as needed
        # Add any other context data
    }
    return render(request, 'topNavigation.html', context)
