from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Product, SellerProfile, Review, Alert, UserRole, Purchase
from .forms import ProductForm, ReviewForm, UserRegistrationForm
from django.db.models import Avg, Count, Q
from django.utils import timezone

def home(request):
    if request.user.is_authenticated:
        try:
            role = request.user.role.role
        except:
            role = 'buyer'
    else:
        role = None

    approved_products = Product.objects.filter(status='approved').order_by('-created_at')[:12]
    
    for product in approved_products:
        if product.remaining_hours() <= 0:
            product.status = 'expired'
            product.save()

    context = {
        'products': approved_products,
        'role': role,
    }
    return render(request, 'home.html', context)

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        role = request.POST.get('role', 'buyer')

        if password != password_confirm:
            messages.error(request, 'Passwords do not match')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        UserRole.objects.create(user=user, role=role, is_approved='pending')

        if role == 'seller':
            SellerProfile.objects.create(user=user, company_name=username)

        messages.success(request, f'Registration successful! Please wait for admin approval to access your {role} account.')
        return redirect('login')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                user_role = user.role
                if user_role.is_approved == 'pending':
                    messages.error(request, 'Your account is pending admin approval. Please try again later.')
                    return redirect('login')
                elif user_role.is_approved == 'rejected':
                    messages.error(request, 'Your account has been rejected by admin.')
                    return redirect('login')
                
                login(request, user)
                return redirect('home')
            except:
                login(request, user)
                return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')

    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def buyer_dashboard(request):
    try:
        role = request.user.role.role
        if role != 'buyer':
            return redirect('home')
    except:
        return redirect('home')

    approved_products = Product.objects.filter(status='approved').order_by('-created_at')
    
    for product in approved_products:
        if product.remaining_hours() <= 0:
            product.status = 'expired'
            product.save()

    alert_level = request.GET.get('alert', '')
    if alert_level:
        if alert_level == 'urgent':
            approved_products = approved_products.filter(
                Q(expiry_datetime__lte=timezone.now() + timezone.timedelta(hours=6)) &
                Q(expiry_datetime__gt=timezone.now())
            )
        elif alert_level == 'soon':
            approved_products = approved_products.filter(
                Q(expiry_datetime__lte=timezone.now() + timezone.timedelta(hours=24)) &
                Q(expiry_datetime__gt=timezone.now() + timezone.timedelta(hours=6))
            )

    context = {
        'products': approved_products,
        'role': 'buyer',
    }
    return render(request, 'buyer_dashboard.html', context)

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, status='approved')
    reviews = product.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.buyer = request.user
            review.save()
            messages.success(request, 'Review posted successfully')
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'form': form,
    }
    return render(request, 'product_detail.html', context)

@login_required
def seller_dashboard(request):
    try:
        role = request.user.role.role
        if role != 'seller':
            return redirect('home')
    except:
        return redirect('home')

    seller_profile = get_object_or_404(SellerProfile, user=request.user)
    products = seller_profile.products.all().order_by('-created_at')

    for product in products:
        if product.remaining_hours() <= 0 and product.status != 'expired':
            product.status = 'expired'
            product.save()

    context = {
        'seller': seller_profile,
        'products': products,
        'role': 'seller',
    }
    return render(request, 'seller_dashboard.html', context)

@login_required
def add_product(request):
    try:
        role = request.user.role.role
        if role != 'seller':
            return redirect('home')
    except:
        return redirect('home')

    seller_profile = get_object_or_404(SellerProfile, user=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = seller_profile
            product.status = 'approved'
            product.save()
            messages.success(request, 'Product added successfully and is now visible to buyers!')
            return redirect('seller_dashboard')
    else:
        form = ProductForm()

    context = {
        'form': form,
        'role': 'seller',
    }
    return render(request, 'add_product.html', context)

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    try:
        role = request.user.role.role
        if role != 'seller':
            return redirect('home')
    except:
        return redirect('home')

    if product.seller.user != request.user:
        return redirect('seller_dashboard')

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully')
            return redirect('seller_dashboard')
    else:
        form = ProductForm(instance=product)

    context = {
        'form': form,
        'product': product,
        'role': 'seller',
    }
    return render(request, 'edit_product.html', context)

@login_required
def admin_dashboard(request):
    try:
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                role = request.user.role.role
                if role != 'admin':
                    return redirect('home')
            except:
                return redirect('home')
    except:
        return redirect('home')

    pending_products = Product.objects.filter(status='pending')
    approved_products = Product.objects.filter(status='approved')
    rejected_products = Product.objects.filter(status='rejected')
    expired_products = Product.objects.filter(status='expired')
    
    pending_users = UserRole.objects.filter(is_approved='pending')
    approved_users = UserRole.objects.filter(is_approved='approved')
    rejected_users = UserRole.objects.filter(is_approved='rejected')

    sellers = SellerProfile.objects.all()

    context = {
        'pending_products': pending_products,
        'approved_products': approved_products,
        'rejected_products': rejected_products,
        'expired_products': expired_products,
        'pending_users': pending_users,
        'approved_users': approved_users,
        'rejected_users': rejected_users,
        'sellers': sellers,
        'role': 'admin',
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
def approve_product(request, product_id):
    try:
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                role = request.user.role.role
                if role != 'admin':
                    return redirect('home')
            except:
                return redirect('home')
    except:
        return redirect('home')

    product = get_object_or_404(Product, id=product_id)
    product.status = 'approved'
    product.save()
    messages.success(request, f'{product.name} has been approved')
    return redirect('admin_dashboard')

@login_required
def reject_product(request, product_id):
    try:
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                role = request.user.role.role
                if role != 'admin':
                    return redirect('home')
            except:
                return redirect('home')
    except:
        return redirect('home')

    product = get_object_or_404(Product, id=product_id)
    product.status = 'rejected'
    product.save()
    messages.error(request, f'{product.name} has been rejected')
    return redirect('admin_dashboard')

@login_required
def seller_alerts(request):
    try:
        role = request.user.role.role
        if role != 'seller':
            return redirect('home')
    except:
        return redirect('home')

    seller_profile = get_object_or_404(SellerProfile, user=request.user)
    seller_products = seller_profile.products.all()

    for product in seller_products:
        check_and_create_alerts(product)

    alerts = Alert.objects.filter(
        product__seller=seller_profile,
        alert_type='seller'
    ).order_by('-created_at')

    context = {
        'alerts': alerts,
        'role': 'seller',
    }
    return render(request, 'seller_alerts.html', context)

@login_required
def mark_alert_read(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id)
    alert.is_read = True
    alert.save()
    return redirect('seller_alerts')

def check_and_create_alerts(product):
    if product.status == 'approved':
        hours = product.remaining_hours()
        
        if hours <= 0:
            product.status = 'expired'
            product.save()
            return

        existing_alert = Alert.objects.filter(
            product=product,
            alert_type='seller',
            alert_level=product.alert_level()
        ).exists()

        if not existing_alert:
            alert_messages = {
                'expired': 'Your product has expired',
                'last_chance': 'Less than 1 hour left',
                'urgent': 'Urgent: Less than 6 hours left',
                'soon': 'Expiring soon: Less than 24 hours',
                'warning': 'Early warning: Less than 48 hours',
                'normal': 'All is normal'
            }

            Alert.objects.create(
                product=product,
                alert_type='seller',
                alert_level=product.alert_level(),
                message=alert_messages.get(product.alert_level(), 'Status update')
            )

@login_required
def approve_user(request, user_id):
    try:
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                role = request.user.role.role
                if role != 'admin':
                    return redirect('home')
            except:
                return redirect('home')
    except:
        return redirect('home')

    user = get_object_or_404(User, id=user_id)
    user_role = get_object_or_404(UserRole, user=user)
    user_role.is_approved = 'approved'
    user_role.approved_at = timezone.now()
    user_role.save()
    
    messages.success(request, f'{user.username} ({user_role.role}) has been approved')
    return redirect('admin_dashboard')

@login_required
def reject_user(request, user_id):
    try:
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                role = request.user.role.role
                if role != 'admin':
                    return redirect('home')
            except:
                return redirect('home')
    except:
        return redirect('home')

    user = get_object_or_404(User, id=user_id)
    user_role = get_object_or_404(UserRole, user=user)
    user_role.is_approved = 'rejected'
    user_role.save()
    
    messages.error(request, f'{user.username} ({user_role.role}) has been rejected')
    return redirect('admin_dashboard')

@login_required
def buy_product(request, product_id):
    try:
        role = request.user.role.role
        if role != 'buyer':
            messages.error(request, 'Only buyers can purchase products')
            return redirect('home')
    except:
        messages.error(request, 'Please set your role as a buyer')
        return redirect('home')

    product = get_object_or_404(Product, id=product_id, status='approved')
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0 or quantity > product.quantity:
            messages.error(request, f'Invalid quantity. Available: {product.quantity}')
            return redirect('product_detail', product.id)
        
        # Create purchase record
        total_price = product.price * quantity
        Purchase.objects.create(
            buyer=request.user,
            product_name=product.name,
            seller_name=product.seller.company_name,
            price=product.price,
            quantity=quantity,
            total_price=total_price
        )
        
        # Reduce product quantity or delete if 0
        product.quantity -= quantity
        if product.quantity <= 0:
            product.delete()
            messages.success(request, f'Successfully purchased {quantity} unit(s) of {product.name}! Product removed from seller.')
        else:
            product.save()
            messages.success(request, f'Successfully purchased {quantity} unit(s) of {product.name}!')
        
        return redirect('buyer_dashboard')
    
    context = {
        'product': product,
        'role': 'buyer',
    }
    return render(request, 'product_detail.html', context)

@login_required
def buyer_history(request):
    try:
        role = request.user.role.role
        if role != 'buyer':
            return redirect('home')
    except:
        return redirect('home')
    
    purchases = Purchase.objects.filter(buyer=request.user).order_by('-purchased_at')
    
    context = {
        'purchases': purchases,
        'role': 'buyer',
    }
    return render(request, 'buyer_history.html', context)
