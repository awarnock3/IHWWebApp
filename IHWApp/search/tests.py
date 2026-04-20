"""
Unit tests for search forms and views
"""
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from datetime import date
from search.forms import ObservationSearchForm
from unittest.mock import patch, MagicMock


class ObservationSearchFormTest(TestCase):
    """Tests for ObservationSearchForm"""
    
    def test_form_valid_with_required_fields(self):
        """Test form is valid with required date fields in YYYY-MM-DD format"""
        form_data = {
            'start_date': '1986-02-01',
            'end_date': '1986-02-28'
        }
        form = ObservationSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_with_wrong_date_format(self):
        """Test form rejects MM/DD/YYYY format"""
        form_data = {
            'start_date': '02/01/1986',
            'end_date': '02/28/1986'
        }
        form = ObservationSearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('start_date', form.errors)
        self.assertIn('end_date', form.errors)
    
    def test_form_invalid_with_missing_dates(self):
        """Test form is invalid without required dates"""
        form = ObservationSearchForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('start_date', form.errors)
        self.assertIn('end_date', form.errors)
    
    def test_form_invalid_with_end_before_start(self):
        """Test form validation catches end date before start date"""
        form_data = {
            'start_date': '1986-02-28',
            'end_date': '1986-02-01'
        }
        form = ObservationSearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_form_valid_with_optional_observer(self):
        """Test form accepts optional observer"""
        form_data = {
            'start_date': '1986-02-01',
            'end_date': '1986-02-28',
            'observer': 'Test Observer'
        }
        form = ObservationSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_date_parsing(self):
        """Test that dates are parsed correctly from YYYY-MM-DD format"""
        form_data = {
            'start_date': '1986-02-09',
            'end_date': '1986-02-10'
        }
        form = ObservationSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['start_date'], date(1986, 2, 9))
        self.assertEqual(form.cleaned_data['end_date'], date(1986, 2, 10))
    
    def test_form_accepts_iso_format(self):
        """Test that YYYY-MM-DD format is correctly accepted"""
        form_data = {
            'start_date': '1985-12-01',
            'end_date': '1986-01-15'
        }
        form = ObservationSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(str(form.cleaned_data['start_date']), '1985-12-01')
        self.assertEqual(str(form.cleaned_data['end_date']), '1986-01-15')


class SearchViewTest(TestCase):
    """Tests for search views"""
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
    
    def test_search_page_loads(self):
        """Test that search page loads successfully"""
        response = self.client.get(reverse('search:search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/search.html')
        self.assertContains(response, 'Search the Archive')
    
    def test_search_form_rendered(self):
        """Test that search form is rendered on page"""
        response = self.client.get(reverse('search:search'))
        self.assertContains(response, 'id_start_date')
        self.assertContains(response, 'id_end_date')
        self.assertContains(response, 'type="date"')
    
    def test_search_redirect_to_results(self):
        """Test that valid search redirects to results"""
        response = self.client.post(reverse('search:search'), {
            'start_date': '1986-02-01',
            'end_date': '1986-02-28'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/search/results/', response.url)
    
    def test_home_redirects_to_search(self):
        """Test that homepage redirects to search"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/search/')
    
    def test_invalid_form_shows_errors(self):
        """Test that invalid form data shows errors"""
        response = self.client.post(reverse('search:search'), {
            'start_date': '1986-02-28',
            'end_date': '1986-02-01'  # End before start
        })
        # Should re-render form with errors, not redirect
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/search.html')
