"""
Unit tests for IHW core models
"""
from django.test import TestCase
from datetime import datetime, date
from core.models import (
    IhwNetwork, IhwSubnet, IhwFiles, IhwFilepath,
    IhwFileFilepath, IhwEphemeris, IdxMetaCommon, IdxMetaIrpol
)


class IhwNetworkModelTest(TestCase):
    """Tests for IhwNetwork model"""
    
    def test_network_str_representation(self):
        """Test string representation of network"""
        network = IhwNetwork(
            id=1,
            netnum=1,
            discipline='ASTR',
            name='Astrometry'
        )
        self.assertEqual(str(network), 'Astrometry (ASTR)')


class IhwEphemerisModelTest(TestCase):
    """Tests for IhwEphemeris model"""
    
    def test_ephemeris_str_representation(self):
        """Test string representation of ephemeris"""
        ephem = IhwEphemeris(
            comet='Halley',
            date=date(1986, 2, 9),
            hour=12.5
        )
        self.assertEqual(str(ephem), 'Halley @ 1986-02-09 12.5h')
    
    def test_ephemeris_str_with_no_hour(self):
        """Test string representation when hour is None"""
        ephem = IhwEphemeris(
            comet='Halley',
            date=date(1986, 2, 9),
            hour=None
        )
        self.assertEqual(str(ephem), 'Halley @ 1986-02-09 0.0h')


class IhwFilesModelTest(TestCase):
    """Tests for IhwFiles model"""
    
    def test_files_str_representation(self):
        """Test string representation of file"""
        file = IhwFiles(filename='test.fit')
        self.assertEqual(str(file), 'test.fit')


class IdxMetaCommonModelTest(TestCase):
    """Tests for IdxMetaCommon model"""
    
    def test_has_file_with_file(self):
        """Test has_file returns True when file exists"""
        network = IhwNetwork(id=1, netnum=1, discipline='ASTR', name='Astrometry')
        file = IhwFiles(fileid=1, filename='test.fit')
        
        obs = IdxMetaCommon(
            network=network,
            date_obs=datetime(1986, 2, 9, 12, 0),
            idxfileid=file,
            observer='Test Observer'
        )
        self.assertTrue(obs.has_file())
    
    def test_has_file_without_file(self):
        """Test has_file returns False when no file"""
        network = IhwNetwork(id=1, netnum=1, discipline='ASTR', name='Astrometry')
        
        obs = IdxMetaCommon(
            network=network,
            date_obs=datetime(1986, 2, 9, 12, 0),
            idxfileid=None,
            observer='Test Observer'
        )
        self.assertFalse(obs.has_file())
    
    def test_str_representation(self):
        """Test string representation of observation"""
        network = IhwNetwork(id=1, netnum=1, discipline='ASTR', name='Astrometry')
        obs = IdxMetaCommon(
            network=network,
            date_obs=datetime(1986, 2, 9, 12, 30),
            observer='Test Observer'
        )
        expected = '1986-02-09 12:30 - ASTR - Test Observer'
        self.assertEqual(str(obs), expected)


class IdxMetaIrpolModelTest(TestCase):
    """Regression tests for schema-backed metadata models"""

    def test_irpol_model_matches_schema_columns(self):
        """IRPOL should only expose columns that exist in the legacy schema."""
        concrete_fields = [
            field.name for field in IdxMetaIrpol._meta.concrete_fields
        ]
        self.assertEqual(
            concrete_fields,
            ['id', 'meta_common', 'syscode', 'observatory_id'],
        )
