"""
Unit tests for search forms and views
"""
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from datetime import date
from pathlib import Path
from search.forms import ObservationSearchForm
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
from tempfile import TemporaryDirectory


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
        """Test form is invalid when no search criteria are provided"""
        form = ObservationSearchForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
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

    def test_form_defaults_end_date_to_start_date(self):
        """Test that missing end date defaults to start date for single-day search"""
        form_data = {
            'start_date': '1986-02-09',
        }
        form = ObservationSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['start_date'], date(1986, 2, 9))
        self.assertEqual(form.cleaned_data['end_date'], date(1986, 2, 9))


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
        self.assertIn(reverse('search:results'), response.url)
    
    def test_home_redirects_to_search(self):
        """Test that homepage redirects to search"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('search:search'))
    
    def test_invalid_form_shows_errors(self):
        """Test that invalid form data shows errors"""
        response = self.client.post(reverse('search:search'), {
            'start_date': '1986-02-28',
            'end_date': '1986-02-01'  # End before start
        })
        # Should re-render form with errors, not redirect
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/search.html')


def mock_metadata_model(count):
    manager = MagicMock()
    manager.filter.return_value.count.return_value = count
    return SimpleNamespace(objects=manager)


class ObservatoryDetailViewTest(TestCase):
    """Tests for observatory detail counts"""

    def setUp(self):
        self.client = Client()
        self.observatory = SimpleNamespace(
            id=42,
            observatory='Test Observatory',
            location='Test Location',
            system='TEST',
            lat=None,
            lon=None,
            telescope=None,
            aperture=None,
            instrument=None,
            subdiscipline=None,
        )

    @patch('core.models.ApxIhwObscodes.objects.get')
    @patch('core.models.IdxMetaPflx', new=mock_metadata_model(7))
    @patch('core.models.IdxMetaNnsn', new=mock_metadata_model(0))
    @patch('core.models.IdxMetaLspn', new=mock_metadata_model(5))
    @patch('core.models.IdxMetaIrsp', new=mock_metadata_model(0))
    @patch('core.models.IdxMetaIrpol', new=mock_metadata_model(0))
    @patch('core.models.IdxMetaIrph', new=mock_metadata_model(4))
    @patch('core.models.IdxMetaIrim', new=mock_metadata_model(0))
    @patch('core.models.IdxMetaAstrom', new=mock_metadata_model(3))
    def test_observatory_detail_shows_all_populated_network_counts(self, mock_get):
        mock_get.return_value = self.observatory

        response = self.client.get(reverse('search:observatory-detail', kwargs={'observatory_id': 42}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This observatory contributed')
        self.assertContains(response, '19')
        self.assertContains(response, 'Astrometry (ASTROM)')
        self.assertContains(response, 'Infrared Photometry (IRPH)')
        self.assertContains(response, 'Large-Scale Phenomena (LSPN)')
        self.assertContains(response, 'Photometry Flux (PFLX)')
        self.assertNotContains(response, 'Near-Nucleus Studies (NNSN)')


class DocumentationViewTest(TestCase):
    """Tests for project-managed documentation views."""

    def setUp(self):
        self.client = Client()

    def test_documentation_page_lists_project_documents(self):
        with TemporaryDirectory() as temp_dir:
            docs_root = Path(temp_dir)
            (docs_root / 'guide.txt').write_text('Guide overview', encoding='utf-8')
            (docs_root / 'subdir').mkdir()
            (docs_root / 'subdir' / 'notes.txt').write_text('Nested notes', encoding='utf-8')
            (docs_root / '.gitkeep').write_text('', encoding='utf-8')

            with override_settings(APP_DOCUMENTS_ROOT=docs_root):
                response = self.client.get(reverse('documentation'))

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Project Documentation')
            self.assertContains(response, 'guide.txt')
            self.assertContains(response, 'subdir/notes.txt')
            self.assertContains(response, '$APP_ROOT/documents')
            self.assertNotContains(response, str(docs_root))
            self.assertNotContains(response, '.gitkeep')

    def test_documentation_file_viewer_renders_text_content(self):
        with TemporaryDirectory() as temp_dir:
            docs_root = Path(temp_dir)
            (docs_root / 'guides').mkdir()
            (docs_root / 'guides' / 'intro.txt').write_text(
                'International Halley Watch notes',
                encoding='utf-8',
            )

            with override_settings(APP_DOCUMENTS_ROOT=docs_root):
                response = self.client.get(
                    reverse(
                        'documentation-file',
                        kwargs={'relative_path': 'guides/intro.txt'},
                    )
                )

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'guides/intro.txt')
            self.assertContains(response, 'International Halley Watch notes')
            self.assertContains(response, '$APP_ROOT/documents/guides/intro.txt')
            self.assertNotContains(response, str(docs_root))

    def test_documentation_file_viewer_blocks_path_traversal(self):
        with TemporaryDirectory() as temp_dir:
            docs_root = Path(temp_dir)
            (docs_root / 'guide.txt').write_text('Guide', encoding='utf-8')

            with override_settings(APP_DOCUMENTS_ROOT=docs_root):
                response = self.client.get('/documentation/../secret.txt/')

            self.assertEqual(response.status_code, 404)
