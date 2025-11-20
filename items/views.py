from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from .models import Item
from .forms import RegisterForm, ItemForm


def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'items/home.html')


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegisterForm()
    
    return render(request, 'items/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'items/login.html')


@login_required(login_url='login')
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required(login_url='login')
def dashboard(request):
    """Main dashboard view with add item form and item list"""
    items = Item.objects.filter(user=request.user)
    
    # Search functionality
    query = request.GET.get('q', '')
    if query:
        items = items.filter(
            Q(item_name__icontains=query) | Q(category__icontains=query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        filtered_items = []
        for item in items:
            if item.get_status() == status_filter:
                filtered_items.append(item)
        items = filtered_items
    
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, 'Item added successfully!')
            return redirect('dashboard')
    else:
        form = ItemForm()
    
    # Count items by status
    all_items = Item.objects.filter(user=request.user)
    expired_count = sum(1 for item in all_items if item.get_status() == 'expired')
    soon_count = sum(1 for item in all_items if item.get_status() == 'soon')
    safe_count = sum(1 for item in all_items if item.get_status() == 'safe')
    
    alerts = [item for item in Item.objects.all() if item.should_alert()]
    
    context = {
        'form': form,
        'items': items,
        'query': query,
        'status_filter': status_filter,
        'expired_count': expired_count,
        'soon_count': soon_count,
        'safe_count': safe_count,
        'alerts': alerts,
    }
    
    return render(request, 'items/dashboard.html', context)


@login_required(login_url='login')
def delete_item(request, item_id):
    """Delete an item"""
    item = get_object_or_404(Item, id=item_id, user=request.user)
    
    if request.method == 'POST':
        item_name = item.item_name
        item.delete()
        messages.success(request, f'"{item_name}" has been deleted.')
        return redirect('dashboard')
    
    return render(request, 'items/delete_item.html', {'item': item})


@login_required(login_url='login')
def edit_item(request, item_id):
    """Edit an item"""
    item = get_object_or_404(Item, id=item_id, user=request.user)
    
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated successfully!')
            return redirect('dashboard')
    else:
        form = ItemForm(instance=item)
    
    return render(request, 'items/edit_item.html', {'form': form, 'item': item})
