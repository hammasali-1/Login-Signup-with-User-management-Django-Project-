from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings

from .models import customers, SiteInfo, ContactMessage
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

# Create your views here.

def index(request):
    if request.session.get('user_id'):
        try:
            u = customers.objects.get(pk=request.session['user_id'])
            if u.role == 'user':
                return redirect('profile')
            return redirect('myfile')
        except customers.DoesNotExist:
            request.session.flush()
    return render(request,'home_page.html')

def myfile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    try:
        user = customers.objects.get(pk=user_id)
    except customers.DoesNotExist:
        request.session.flush()
        return redirect('index')
    if user.role == 'user':
        return redirect('profile')
    q = request.GET.get('q','').strip()
    base_qs = customers.objects.filter(is_deleted=False)
    if user.role == 'manager':
        base_qs = base_qs.filter(role='user')
    objects = base_qs
    if q:
        objects = objects.filter(Q(username__icontains=q) | Q(email__icontains=q))
    if request.GET.get('format') == 'json':
        data = [{'id': o.id, 'username': o.username, 'email': o.email, 'role': o.role, 'is_active': o.is_active} for o in objects]
        return JsonResponse({'results': data, 'role': user.role, 'acting_id': user.id})
    total = base_qs.count()
    active = base_qs.filter(is_active=True).count()
    inactive = base_qs.filter(is_active=False).count()
    return render(request, 'myfile.html', {
        'obj': objects,
        'current_user': user,
        'current_role': user.role,
        'q': q,
        'counts': {'total': total, 'active': active, 'inactive': inactive}
    })

@csrf_protect
def login(request):

    if request.session.get('user_id'):
        try:
            u = customers.objects.get(pk=request.session['user_id'])
            if u.role == 'user':
                return redirect('profile')
            return redirect('myfile')
        except customers.DoesNotExist:
            request.session.flush()

    if request.method == 'POST':
        email = request.POST['Email']
        password = request.POST['Password']
        next_url = request.POST.get('next')
        try:
            user = customers.objects.get(email=email, password=password)
            if user.is_deleted:
                return render(request, 'login_page.html', {'error': 'Your account has been deleted.'})
            if not user.is_active:
                return render(request, 'login_page.html', {'error': 'Your account is inactive. Please contact admin.'})

            #creating session
            request.session['user_id'] = user.id
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            if user.role == 'user':
                return redirect('profile')
            return redirect('myfile')
        except customers.DoesNotExist:
            return render(request, 'login_page.html', {'error': 'Invalid credentials'})

        # For built in Model Auth
        # user = authenticate(request,username=email, password=password)
        # if user is not None:
        #     login(request, user)
        #     return redirect('myfile')
        # else:
        #     return render(request,'login_page.html', {'mes':'Wrong Credentials'})
        
    #     # obj = customers.objects.create(name = name ,email = email)
    #     # Above method OR Below method to store
    #     obj = customers()
    #     obj.email = email
    #     obj.password = password

    #     try:
    #         obj.save()
    #         # objects=customers.objects.filter(email='waqas123@gmail.com')  #Can use filter to show or get specific or required results, filter can provide muliple results
    #         # objects=customers.objects.get(email='waqas123@gmail.com')  #Can use get to show or get specific or required result, get can only provide one result , cannot use loop to show the get result.
    #         # return HttpResponse("Successfully Added!")
    #         return redirect('myfile')
    #     except:
    #         return HttpResponse("Failed to Login")
    else:
        return render(request, 'login_page.html')
    
    # if request.user.is_authenticated:
    #     return redirect('myfile')
    # else:
    #     return render(request, 'login_page.html')

@csrf_protect
def signup(request):
    if request.method == 'POST':
        username = request.POST['Username']
        email = request.POST['Email']
        password = request.POST['Password']
        if customers.objects.filter(username=username).exists() or customers.objects.filter(email=email).exists():
            return render(request, 'signup_page.html', {'mes':'Username or Email already exists'})
        obj = customers()
        obj.username = username
        obj.email = email
        obj.password = password
        obj.is_active = True
        obj.role = 'user'
        try:
            if customers.objects.count() == 0:
                obj.role = 'admin'
        except Exception:
            pass
        try:
            obj.save()
            messages.success(request, 'Account created')
            return redirect('login')
        except:
            return render(request, 'signup_page.html', {'mes':'Something Wrong!'})
    return render(request,'signup_page.html')
    
def delete(request,id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    acting = customers.objects.get(pk=user_id)
    if acting.role != 'admin':
        return redirect('myfile')
    obj = customers.objects.get(pk=id)
    if obj.id == acting.id:
        return redirect('myfile')
    obj.is_deleted = True
    obj.is_active = False
    obj.save()
    return redirect('myfile')

@csrf_protect
def update(request,id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    acting = customers.objects.get(pk=user_id)
    if request.method == 'POST':
        myid=request.POST['Id']
        obj = customers.objects.get(pk=myid)
        new_username = request.POST['Username']
        new_email = request.POST['Email']
        if customers.objects.filter(username=new_username).exclude(pk=obj.pk).exists() or customers.objects.filter(email=new_email).exclude(pk=obj.pk).exists():
            data = {'obj':obj , 'id':id, 'current_role': acting.role, 'current_user': acting, 'editing_self': obj.id == acting.id, 'error': 'Username or Email already exists'}
            return render(request,'update_form.html',data)
        obj.username = new_username
        obj.email = new_email
        obj.password = request.POST['Password']
        if acting.role == 'admin':
            if obj.id != acting.id:
                role_val = request.POST.get('Role')
                if role_val in ['admin','manager','user']:
                    obj.role = role_val
        else:
            if obj.role != 'user':
                return redirect('myfile')
        
        obj.save()
        messages.success(request, 'User updated')
        return redirect('myfile')

    obj = customers.objects.get(pk=id)
    data = {'obj':obj , 'id':id, 'current_role': acting.role, 'current_user': acting, 'editing_self': obj.id == acting.id}
    return render(request,'update_form.html',data)

@csrf_protect
def delete_account(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    try:
        user = customers.objects.get(pk=user_id)
    except customers.DoesNotExist:
        request.session.flush()
        return redirect('index')
    if request.method == 'POST':
        if user.role == 'user':
            user.is_deleted = True
            user.is_active = False
            user.save()
            request.session.flush()
            return redirect('index')
    return redirect('profile')

def stats(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    try:
        acting = customers.objects.get(pk=user_id)
    except customers.DoesNotExist:
        request.session.flush()
        return redirect('index')
    if acting.role == 'user':
        return redirect('profile')
    base_qs = customers.objects.filter(is_deleted=False)
    del_qs = customers.objects.filter(is_deleted=True)
    if acting.role == 'manager':
        base_qs = base_qs.filter(role='user')
        del_qs = del_qs.filter(role='user')
    total = base_qs.count()
    active = base_qs.filter(is_active=True).count()
    inactive = base_qs.filter(is_active=False).count()
    deleted = del_qs.count()
    role_counts = {}
    if acting.role == 'admin':
        for r in ['admin','manager','user']:
            role_counts[r] = base_qs.filter(role=r).count()
    else:
        role_counts['user'] = base_qs.filter(role='user').count()
    return render(request,'stats.html',{
        'current_role': acting.role,
        'current_user': acting,
        'total': total,
        'active': active,
        'inactive': inactive,
        'deleted': deleted,
        'role_counts': role_counts
    })

def mylogout(request):
    # logout(request)
    request.session.flush()
    return redirect('index')

@csrf_protect
def create_user(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    try:
        acting = customers.objects.get(pk=user_id)
    except customers.DoesNotExist:
        request.session.flush()
        return redirect('index')
    if acting.role not in ('admin','manager'):
        return redirect('profile')
    if request.method == 'POST':
        username = request.POST.get('Username','')
        email = request.POST.get('Email','')
        password = request.POST.get('Password','')
        role_val = request.POST.get('Role','user')
        if customers.objects.filter(username=username).exists() or customers.objects.filter(email=email).exists():
            messages.error(request, 'Username or Email already exists')
            return redirect('myfile')
        obj = customers()
        obj.username = username
        obj.email = email
        obj.password = password
        obj.is_active = True
        if acting.role == 'admin' and role_val in ('admin','manager','user'):
            obj.role = role_val
        else:
            obj.role = 'user'
        try:
            obj.save()
            messages.success(request, 'User created')
        except:
            messages.error(request, 'Failed to create user')
        return redirect('myfile')
    return redirect('myfile')

def profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    try:
        user = customers.objects.get(pk=user_id)
    except customers.DoesNotExist:
        request.session.flush()
        return redirect('index')
    return render(request,'profile.html',{'user':user, 'current_user': user, 'current_role': user.role})

def contact(request):
    si = SiteInfo.objects.first()
    if not si:
        si = SiteInfo.objects.create()
    user_id = request.session.get('user_id')
    current_user = None
    if user_id:
        try:
            current_user = customers.objects.get(pk=user_id)
        except customers.DoesNotExist:
            request.session.flush()
    if request.method == 'POST' and current_user and request.POST.get('action') == 'send':
        subject = request.POST.get('subject','').strip()
        msg = request.POST.get('message','').strip()
        if msg:
            cm = ContactMessage()
            cm.user = current_user
            cm.username = current_user.username
            cm.email = current_user.email
            cm.subject = subject or None
            cm.message = msg
            try:
                cm.save()
                messages.success(request,'Message sent')
            except Exception:
                messages.error(request,'Failed to send message')
        return redirect('contact')
    return render(request,'contact.html',{'site': si, 'current_user': current_user})

def about(request):
    si = SiteInfo.objects.first()
    if not si:
        si = SiteInfo.objects.create()
    user_id = request.session.get('user_id')
    current_user = None
    if user_id:
        try:
            current_user = customers.objects.get(pk=user_id)
        except customers.DoesNotExist:
            request.session.flush()
    return render(request,'about.html',{'site': si, 'current_user': current_user})

@csrf_protect
def bulk_action(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    try:
        acting = customers.objects.get(pk=user_id)
    except customers.DoesNotExist:
        request.session.flush()
        return redirect('index')
    if acting.role != 'admin':
        return redirect('myfile')
    if request.method == 'POST':
        ids = request.POST.getlist('ids')
        action = request.POST.get('action')
        if str(acting.id) in ids:
            ids = [i for i in ids if i != str(acting.id)]
        if ids and action in ('delete','make_admin','make_manager','make_user','activate','deactivate'):
            qs = customers.objects.filter(id__in=ids)
            if action == 'delete':
                qs.update(is_deleted=True, is_active=False)
            elif action == 'make_admin':
                qs.update(role='admin')
            elif action == 'make_manager':
                qs.update(role='manager')
            elif action == 'make_user':
                qs.update(role='user')
            elif action == 'activate':
                qs.update(is_active=True)
            elif action == 'deactivate':
                qs.update(is_active=False)
        return redirect('myfile')
    return redirect('myfile')

@csrf_protect
def toggle_status(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'ok': False}, status=401)
    try:
        acting = customers.objects.get(pk=user_id)
    except customers.DoesNotExist:
        request.session.flush()
        return JsonResponse({'ok': False}, status=401)
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)
    target_id = request.POST.get('id')
    val = request.POST.get('is_active')
    try:
        target = customers.objects.get(pk=target_id)
    except customers.DoesNotExist:
        return JsonResponse({'ok': False}, status=404)
    if target.id == acting.id:
        return JsonResponse({'ok': False}, status=403)
    if acting.role == 'manager' and target.role != 'user':
        return JsonResponse({'ok': False}, status=403)
    target.is_active = True if str(val).lower() in ('1','true','yes','on') else False
    target.save()
    return JsonResponse({'ok': True, 'id': target.id, 'is_active': target.is_active})

@csrf_protect
def edit_contact(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    acting = customers.objects.get(pk=user_id)
    if acting.role != 'admin':
        return redirect('contact')
    if request.method == 'POST':
        si = SiteInfo.objects.first()
        if not si:
            si = SiteInfo()
        si.contact_email = request.POST.get('email','')
        si.contact_phone = request.POST.get('phone','')
        si.contact_address = request.POST.get('address','')
        si.contact_description = request.POST.get('description','')
        try:
            si.save()
            messages.success(request,'Contact updated')
        except Exception:
            messages.error(request,'Failed to update contact')
    return redirect('contact')

@csrf_protect
def edit_about(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    acting = customers.objects.get(pk=user_id)
    if acting.role != 'admin':
        return redirect('about')
    if request.method == 'POST':
        si = SiteInfo.objects.first()
        if not si:
            si = SiteInfo()
        si.about_title = request.POST.get('title','About Us')
        si.about_content = request.POST.get('content','')
        try:
            si.save()
            messages.success(request,'About updated')
        except Exception:
            messages.error(request,'Failed to update about')
    return redirect('about')

def inbox(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    acting = customers.objects.get(pk=user_id)
    if acting.role not in ('admin','manager'):
        return redirect('myfile')
    q = request.GET.get('q','').strip()
    role = request.GET.get('role','').strip()
    start = request.GET.get('start','').strip()
    end = request.GET.get('end','').strip()
    msgs = ContactMessage.objects.filter(is_deleted=False)
    if acting.role == 'manager':
        msgs = msgs.filter(user__role='user')
    if role in ('admin','manager','user'):
        msgs = msgs.filter(user__role=role)
    if q:
        msgs = msgs.filter(Q(username__icontains=q) | Q(email__icontains=q) | Q(subject__icontains=q) | Q(message__icontains=q))
    if start:
        try:
            from datetime import datetime
            sdt = datetime.fromisoformat(start)
            msgs = msgs.filter(created_at__gte=sdt)
        except Exception:
            pass
    if end:
        try:
            from datetime import datetime
            edt = datetime.fromisoformat(end)
            msgs = msgs.filter(created_at__lte=edt)
        except Exception:
            pass
    total = msgs.count()
    read = msgs.filter(is_read=True).count()
    unread = msgs.filter(is_read=False).count()
    resolved = msgs.filter(is_resolved=True).count()
    unresolved = msgs.filter(is_resolved=False).count()
    deleted_qs = ContactMessage.objects.filter(is_deleted=True)
    if acting.role == 'manager':
        deleted_qs = deleted_qs.filter(user__role='user')
    deleted = deleted_qs.count()
    return render(request,'inbox.html',{
        'messages_list': msgs.order_by('-created_at')[:500],
        'stats': {'total': total,'read': read,'unread': unread,'resolved': resolved,'unresolved': unresolved,'deleted': deleted},
        'q': q,
        'role': role,
        'start': start,
        'end': end,
        'current_user': acting,
        'current_role': acting.role
    })

def inbox_data(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'ok': False}, status=401)
    acting = customers.objects.get(pk=user_id)
    if acting.role not in ('admin','manager'):
        return JsonResponse({'ok': False}, status=403)
    q = request.GET.get('q','').strip()
    role = request.GET.get('role','').strip()
    start = request.GET.get('start','').strip()
    end = request.GET.get('end','').strip()
    base_qs = ContactMessage.objects.filter(is_deleted=False)
    if acting.role == 'manager':
        base_qs = base_qs.filter(user__role='user')
    if role in ('admin','manager','user'):
        base_qs = base_qs.filter(user__role=role)
    if q:
        base_qs = base_qs.filter(Q(username__icontains=q) | Q(email__icontains=q) | Q(subject__icontains=q) | Q(message__icontains=q))
    if start:
        try:
            from datetime import datetime
            sdt = datetime.fromisoformat(start)
            base_qs = base_qs.filter(created_at__gte=sdt)
        except Exception:
            pass
    if end:
        try:
            from datetime import datetime
            edt = datetime.fromisoformat(end)
            base_qs = base_qs.filter(created_at__lte=edt)
        except Exception:
            pass
    total = base_qs.count()
    read = base_qs.filter(is_read=True).count()
    unread = base_qs.filter(is_read=False).count()
    resolved = base_qs.filter(is_resolved=True).count()
    unresolved = base_qs.filter(is_resolved=False).count()
    msgs = base_qs.order_by('-created_at')[:200]
    deleted_qs = ContactMessage.objects.filter(is_deleted=True)
    if acting.role == 'manager':
        deleted_qs = deleted_qs.filter(user__role='user')
    deleted = deleted_qs.count()
    out = []
    for m in msgs:
        out.append({
            'id': m.id,
            'username': m.username or '-',
            'email': m.email or '-',
            'subject': m.subject or '-',
            'message': m.message,
            'created_at': m.created_at.strftime('%Y-%m-%d %H:%M'),
            'is_read': m.is_read,
            'is_resolved': m.is_resolved,
            'user_role': (m.user.role if m.user else '-')
        })
    return JsonResponse({'ok': True, 'stats': {'total': total,'read': read,'unread': unread,'resolved': resolved,'unresolved': unresolved,'deleted': deleted}, 'messages': out})

def inbox_user(request, user_id):
    acting_id = request.session.get('user_id')
    if not acting_id:
        return redirect('login')
    acting = customers.objects.get(pk=acting_id)
    if acting.role not in ('admin','manager'):
        return redirect('myfile')
    msgs = ContactMessage.objects.filter(is_deleted=False, user_id=user_id)
    target_user = None
    try:
        target_user = customers.objects.get(pk=user_id)
    except customers.DoesNotExist:
        target_user = None
    if acting.role == 'manager':
        if not target_user or target_user.role != 'user':
            return redirect('inbox')
    total = msgs.count()
    read = msgs.filter(is_read=True).count()
    unread = msgs.filter(is_read=False).count()
    resolved = msgs.filter(is_resolved=True).count()
    unresolved = msgs.filter(is_resolved=False).count()
    deleted = ContactMessage.objects.filter(is_deleted=True, user_id=user_id).count()
    user = target_user
    return render(request,'inbox_user.html',{
        'messages_list': msgs.order_by('-created_at')[:500],
        'stats': {'total': total,'read': read,'unread': unread,'resolved': resolved,'unresolved': unresolved,'deleted': deleted},
        'user': user,
        'current_user': acting,
        'current_role': acting.role
    })

@csrf_protect
def inbox_bulk_action(request):
    acting_id = request.session.get('user_id')
    if not acting_id:
        return redirect('login')
    acting = customers.objects.get(pk=acting_id)
    if acting.role not in ('admin','manager'):
        return redirect('myfile')
    if request.method == 'POST':
        ids = request.POST.getlist('ids')
        action = request.POST.get('action')
        qs = ContactMessage.objects.filter(id__in=ids)
        if acting.role == 'manager':
            qs = qs.filter(user__role='user')
        if action == 'delete':
            qs.update(is_deleted=True)
        elif action == 'read':
            qs.update(is_read=True)
        elif action == 'unread':
            qs.update(is_read=False)
        elif action == 'resolve':
            qs.update(is_resolved=True)
        elif action == 'unresolve':
            qs.update(is_resolved=False)
    return redirect('inbox')

@csrf_protect
def inbox_delete_message(request,id):
    acting_id = request.session.get('user_id')
    if not acting_id:
        return redirect('login')
    acting = customers.objects.get(pk=acting_id)
    if acting.role not in ('admin','manager'):
        return redirect('myfile')
    try:
        m = ContactMessage.objects.get(pk=id)
        if acting.role == 'manager':
            if not m.user or m.user.role != 'user':
                return redirect('inbox')
        m.is_deleted = True
        m.save()
    except ContactMessage.DoesNotExist:
        pass
    return redirect('inbox')

@csrf_protect
def inbox_delete_user(request,user_id):
    acting_id = request.session.get('user_id')
    if not acting_id:
        return redirect('login')
    acting = customers.objects.get(pk=acting_id)
    if acting.role not in ('admin','manager'):
        return redirect('myfile')
    if acting.role == 'manager':
        try:
            target = customers.objects.get(pk=user_id)
        except customers.DoesNotExist:
            return redirect('inbox')
        if target.role != 'user':
            return redirect('inbox')
    ContactMessage.objects.filter(user_id=user_id).update(is_deleted=True)
    return redirect('inbox')

@csrf_protect
def upload_profile_image(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    try:
        user = customers.objects.get(pk=user_id)
    except customers.DoesNotExist:
        request.session.flush()
        return redirect('index')
    if request.method == 'POST' and request.FILES.get('image'):
        if user.profile_image:
            try:
                user.profile_image.delete(save=False)
            except Exception:
                pass
        user.profile_image = request.FILES['image']
        user.save()
    return redirect('profile')

@csrf_protect
def delete_profile_image(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    try:
        user = customers.objects.get(pk=user_id)
    except customers.DoesNotExist:
        request.session.flush()
        return redirect('index')
    if request.method == 'POST':
        if user.profile_image:
            try:
                user.profile_image.delete(save=False)
            except Exception:
                pass
        user.profile_image = None
        user.save()
    return redirect('profile')

@csrf_protect
def change_password(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    try:
        user = customers.objects.get(pk=user_id)
    except customers.DoesNotExist:
        request.session.flush()
        return redirect('index')
    if request.method == 'POST':
        old = request.POST.get('Old','')
        new = request.POST.get('New','')
        conf = request.POST.get('Confirm','')
        if not old or not new or not conf:
            return render(request,'profile.html',{'user':user,'pw_error':'All fields are required'})
        if new != conf:
            return render(request,'profile.html',{'user':user,'pw_error':'New and Confirm do not match'})
        if user.password != old:
            return render(request,'profile.html',{'user':user,'pw_error':'Old password is incorrect'})
        user.password = new
        user.save()
        return render(request,'profile.html',{'user':user,'pw_success':'Password updated'})
    return redirect('profile')

@csrf_protect
def set_theme(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'ok': False}, status=401)
    try:
        acting = customers.objects.get(pk=user_id)
    except customers.DoesNotExist:
        request.session.flush()
        return JsonResponse({'ok': False}, status=401)
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)
    theme = request.POST.get('theme')
    if theme not in ('light','dark'):
        return JsonResponse({'ok': False}, status=400)
    acting.theme = theme
    acting.save()
    return JsonResponse({'ok': True, 'theme': theme})
