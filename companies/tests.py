from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Company, CompanyMembership, CompanySettings


class CompanyModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_company_creation(self):
        """Тест создания компании"""
        company = Company.objects.create(
            name='Тестовая компания',
            company_type='LLC',
            owner=self.user
        )
        
        self.assertEqual(company.name, 'Тестовая компания')
        self.assertEqual(company.company_type, 'LLC')
        self.assertEqual(company.owner, self.user)
        self.assertTrue(company.is_active)
        self.assertIsNotNone(company.slug)
    
    def test_slug_generation(self):
        """Тест генерации slug"""
        company = Company.objects.create(
            name='Моя Компания',
            company_type='LLC',
            owner=self.user
        )
        
        self.assertIsNotNone(company.slug)
        self.assertTrue(len(company.slug) > 0)
    
    def test_membership_creation(self):
        """Тест создания членства"""
        company = Company.objects.create(
            name='Тестовая компания',
            company_type='LLC',
            owner=self.user
        )
        
        membership = CompanyMembership.objects.create(
            company=company,
            user=self.user,
            role='owner'
        )
        
        self.assertEqual(membership.company, company)
        self.assertEqual(membership.user, self.user)
        self.assertEqual(membership.role, 'owner')
        self.assertTrue(membership.can_manage_users)
        self.assertTrue(membership.can_manage_orders)


class CompanyViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.company = Company.objects.create(
            name='Тестовая компания',
            company_type='LLC',
            owner=self.user
        )
        
        CompanyMembership.objects.create(
            company=self.company,
            user=self.user,
            role='owner'
        )
    
    def test_company_select_view(self):
        """Тест страницы выбора компании"""
        response = self.client.get(reverse('companies:select'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Вход в систему')
    
    def test_company_login_view(self):
        """Тест страницы входа в компанию"""
        response = self.client.get(
            reverse('companies:login', kwargs={'company_slug': self.company.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.company.name)
    
    def test_company_dashboard_requires_login(self):
        """Тест что дашборд требует авторизации"""
        response = self.client.get(
            reverse('companies:dashboard', kwargs={'company_slug': self.company.slug})
        )
        self.assertRedirects(response, reverse('companies:select'))
    
    def test_company_dashboard_with_login(self):
        """Тест дашборда с авторизованным пользователем"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('companies:dashboard', kwargs={'company_slug': self.company.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Дашборд компании')
