from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Item
from datetime import date, timedelta


class UserRegistrationTest(TestCase):
    """Test user registration functionality"""

    def setUp(self):
        self.client = Client()

    def test_registration_page_loads(self):
        """Test that registration page loads successfully"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'items/register.html')

    def test_user_registration_success(self):
        """Test successful user registration"""
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        })
        
        # Check user was created
        self.assertTrue(User.objects.filter(username='testuser').exists())
        
        # Check redirect to login
        self.assertRedirects(response, reverse('login'))

    def test_registration_password_mismatch(self):
        """Test registration fails with mismatched passwords"""
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'password_confirm': 'wrongpass'
        })
        
        # Check user was not created
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_registration_duplicate_email(self):
        """Test registration fails with duplicate email"""
        # Create first user
        User.objects.create_user(
            username='user1',
            email='test@example.com',
            password='pass123'
        )
        
        # Try to register with same email
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        })
        
        # Check new user was not created
        self.assertEqual(User.objects.filter(email='test@example.com').count(), 1)


class UserLoginTest(TestCase):
    """Test user login functionality"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

    def test_login_page_loads(self):
        """Test that login page loads successfully"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'items/login.html')

    def test_login_success(self):
        """Test successful login"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Check redirect to dashboard
        self.assertRedirects(response, reverse('dashboard'))
        
        # Check user is authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_wrong_password(self):
        """Test login fails with wrong password"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        
        # Check user is not authenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout(self):
        """Test logout functionality"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        
        self.assertRedirects(response, reverse('home'))


class ItemModelTest(TestCase):
    """Test Item model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_item_creation(self):
        """Test item creation"""
        item = Item.objects.create(
            user=self.user,
            item_name='Milk',
            category='dairy',
            expiry_date=date.today() + timedelta(days=5),
            quantity=2
        )
        
        self.assertEqual(item.item_name, 'Milk')
        self.assertEqual(item.user, self.user)

    def test_days_left_calculation(self):
        """Test days left calculation"""
        # Item expiring in 5 days
        item = Item.objects.create(
            user=self.user,
            item_name='Milk',
            category='dairy',
            expiry_date=date.today() + timedelta(days=5),
            quantity=1
        )
        
        self.assertEqual(item.days_left(), 5)

    def test_status_safe(self):
        """Test status returns 'safe'"""
        item = Item.objects.create(
            user=self.user,
            item_name='Milk',
            category='dairy',
            expiry_date=date.today() + timedelta(days=5),
            quantity=1
        )
        
        self.assertEqual(item.get_status(), 'safe')

    def test_status_soon(self):
        """Test status returns 'soon'"""
        item = Item.objects.create(
            user=self.user,
            item_name='Milk',
            category='dairy',
            expiry_date=date.today() + timedelta(days=2),
            quantity=1
        )
        
        self.assertEqual(item.get_status(), 'soon')

    def test_status_expired(self):
        """Test status returns 'expired'"""
        item = Item.objects.create(
            user=self.user,
            item_name='Milk',
            category='dairy',
            expiry_date=date.today() - timedelta(days=1),
            quantity=1
        )
        
        self.assertEqual(item.get_status(), 'expired')


class DashboardViewTest(TestCase):
    """Test dashboard view"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test items
        Item.objects.create(
            user=self.user,
            item_name='Milk',
            category='dairy',
            expiry_date=date.today() + timedelta(days=5),
            quantity=1
        )
        Item.objects.create(
            user=self.user,
            item_name='Tomato',
            category='vegetables',
            expiry_date=date.today() + timedelta(days=2),
            quantity=3
        )

    def test_dashboard_requires_login(self):
        """Test that dashboard requires login"""
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('dashboard'))

    def test_dashboard_loads_for_authenticated_user(self):
        """Test that dashboard loads for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'items/dashboard.html')

    def test_dashboard_shows_user_items(self):
        """Test that dashboard shows user's items"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        self.assertContains(response, 'Milk')
        self.assertContains(response, 'Tomato')


class ItemCRUDTest(TestCase):
    """Test item Create, Read, Update, Delete"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_add_item(self):
        """Test adding an item"""
        response = self.client.post(reverse('dashboard'), {
            'item_name': 'Milk',
            'category': 'dairy',
            'expiry_date': date.today() + timedelta(days=5),
            'quantity': 2,
            'notes': 'Test note'
        })
        
        # Check item was created
        self.assertTrue(Item.objects.filter(item_name='Milk').exists())

    def test_delete_item(self):
        """Test deleting an item"""
        item = Item.objects.create(
            user=self.user,
            item_name='Milk',
            category='dairy',
            expiry_date=date.today() + timedelta(days=5),
            quantity=1
        )
        
        response = self.client.post(reverse('delete_item', args=[item.id]))
        
        # Check item was deleted
        self.assertFalse(Item.objects.filter(id=item.id).exists())

    def test_edit_item(self):
        """Test editing an item"""
        item = Item.objects.create(
            user=self.user,
            item_name='Milk',
            category='dairy',
            expiry_date=date.today() + timedelta(days=5),
            quantity=1
        )
        
        response = self.client.post(reverse('edit_item', args=[item.id]), {
            'item_name': 'Yogurt',
            'category': 'dairy',
            'expiry_date': date.today() + timedelta(days=3),
            'quantity': 2,
            'notes': 'Updated'
        })
        
        # Check item was updated
        item.refresh_from_db()
        self.assertEqual(item.item_name, 'Yogurt')
        self.assertEqual(item.quantity, 2)


class SearchFilterTest(TestCase):
    """Test search and filter functionality"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create items with different statuses
        Item.objects.create(
            user=self.user,
            item_name='Milk',
            category='dairy',
            expiry_date=date.today() + timedelta(days=5)
        )
        Item.objects.create(
            user=self.user,
            item_name='Tomato',
            category='vegetables',
            expiry_date=date.today() + timedelta(days=1)
        )
        Item.objects.create(
            user=self.user,
            item_name='Cheese',
            category='dairy',
            expiry_date=date.today() - timedelta(days=1)
        )
        
        self.client.login(username='testuser', password='testpass123')

    def test_search_by_item_name(self):
        """Test searching by item name"""
        response = self.client.get(reverse('dashboard'), {'q': 'Milk'})
        
        self.assertContains(response, 'Milk')

    def test_filter_by_status_safe(self):
        """Test filtering by safe status"""
        response = self.client.get(reverse('dashboard'), {'status': 'safe'})
        
        self.assertContains(response, 'Milk')

    def test_filter_by_status_expired(self):
        """Test filtering by expired status"""
        response = self.client.get(reverse('dashboard'), {'status': 'expired'})
        
        self.assertContains(response, 'Cheese')
