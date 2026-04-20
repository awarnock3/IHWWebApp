# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class IdxMetaCommon(models.Model):
    network = models.ForeignKey('IhwNetwork', models.DO_NOTHING, db_comment='FK to ihw_network.id')
    date_obs = models.DateTimeField(db_comment='UTC observation datetime')
    net_num = models.IntegerField(db_comment='Discipline-specific observation identifier')
    syscode = models.CharField(max_length=8, db_comment='IHW system code from FITS SYSTEM')
    observer = models.CharField(max_length=64)
    note_flag = models.IntegerField(db_comment='1 if notes are present')
    note = models.TextField(blank=True, null=True)
    object = models.CharField(max_length=24)
    idxfileid = models.ForeignKey('IhwFiles', models.DO_NOTHING, db_column='idxfileid', blank=True, null=True, db_comment='FK to ihw_files.fileid (NULL if no data file)')
    linenum = models.IntegerField(db_comment='Line number within source file')

    class Meta:
        managed = False
        db_table = 'idx_meta_common'
        unique_together = (('network', 'idxfileid', 'linenum'),)
        db_table_comment = 'Cross-discipline common metadata for all IHW networks'


class IhwNetwork(models.Model):
    netnum = models.IntegerField()
    discipline = models.CharField(max_length=8)
    name = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = 'ihw_network'
        db_table_comment = 'Master list of IHW Network disciplines'


class IhwSubnet(models.Model):
    subnet = models.CharField(unique=True, max_length=16)
    subnet_name = models.CharField(max_length=32, blank=True, null=True)
    discipline = models.ForeignKey(IhwNetwork, models.DO_NOTHING, db_column='discipline')

    class Meta:
        managed = False
        db_table = 'ihw_subnet'
        db_table_comment = 'Master list of IHW discipline subnets'


class IhwFiles(models.Model):
    fileid = models.AutoField(primary_key=True)
    filename = models.CharField(max_length=64)
    subnet = models.ForeignKey(IhwSubnet, models.DO_NOTHING)
    type = models.CharField(max_length=16)
    arch_ver = models.CharField(max_length=8)
    digest = models.CharField(unique=True, max_length=32)
    filesize = models.BigIntegerField(db_comment='File size in bytes')

    class Meta:
        managed = False
        db_table = 'ihw_files'
        db_table_comment = 'Master list of unique archive files, identified by MD5 digest'


class IhwFileFilepath(models.Model):
    fileid = models.ForeignKey(IhwFiles, models.DO_NOTHING, db_column='fileid')
    filepathid = models.ForeignKey('IhwFilepath', models.DO_NOTHING, db_column='filepathid')

    class Meta:
        managed = False
        db_table = 'ihw_file_filepath'
        unique_together = (('fileid', 'filepathid'),)
        db_table_comment = 'Utility link table between files and file paths'


class IhwFilepath(models.Model):
    dirpath = models.CharField(unique=True, max_length=512, db_comment='Directory path relative to archive root, no leading or trailing slash')

    class Meta:
        managed = False
        db_table = 'ihw_filepath'
        db_table_comment = 'Directory paths for archive files (relative to configured root)'


class IhwEphemeris(models.Model):
    comet = models.CharField(max_length=9)
    fileid = models.ForeignKey(IhwFiles, models.DO_NOTHING, db_column='fileid')
    date = models.DateField()
    year = models.SmallIntegerField(blank=True, null=True)
    month = models.IntegerField(blank=True, null=True)
    day = models.IntegerField(blank=True, null=True)
    hour = models.FloatField(blank=True, null=True, db_comment='Decimal hours (UT)')
    jday = models.FloatField(blank=True, null=True, db_comment='Julian Date')
    ra = models.FloatField(blank=True, null=True, db_comment='RA decimal degrees (J2000)')
    decl = models.FloatField(blank=True, null=True, db_comment='Dec decimal degrees (J2000)')
    delta = models.FloatField(blank=True, null=True, db_comment='Geocentric distance (AU)')
    deldot = models.FloatField(blank=True, null=True, db_comment='Geocentric radial velocity (km/s)')
    r = models.FloatField(blank=True, null=True, db_comment='Heliocentric distance (AU)')
    rdot = models.FloatField(blank=True, null=True, db_comment='Heliocentric radial velocity (km/s)')
    theta = models.FloatField(blank=True, null=True, db_comment='Solar elongation (deg)')
    beta = models.FloatField(blank=True, null=True, db_comment='Solar latitude (deg)')
    moon = models.FloatField(blank=True, null=True, db_comment='Lunar distance (deg)')
    psang = models.FloatField(blank=True, null=True, db_comment='Position angle sun-comet (deg)')
    psamv = models.FloatField(blank=True, null=True, db_comment='Position angle comet velocity (deg)')

    class Meta:
        managed = False
        db_table = 'ihw_ephemeris'
        db_table_comment = 'IHW comet ephemeris data'
