"""
IHW Core Models - International Halley Watch Archive
Generated from existing MariaDB schema - DO NOT MIGRATE
All models have managed=False to preserve legacy database
"""
from django.db import models
from django.urls import reverse


class IhwNetwork(models.Model):
    """Master list of 9 IHW Network disciplines"""
    netnum = models.IntegerField()
    discipline = models.CharField(max_length=8)
    name = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = 'ihw_network'
        db_table_comment = 'Master list of IHW Network disciplines'

    def __str__(self):
        return f"{self.name} ({self.discipline})"


class IhwSubnet(models.Model):
    """Subdisciplines within each network"""
    subnet = models.CharField(unique=True, max_length=16)
    subnet_name = models.CharField(max_length=32, blank=True, null=True)
    discipline = models.ForeignKey(IhwNetwork, models.DO_NOTHING, db_column='discipline')

    class Meta:
        managed = False
        db_table = 'ihw_subnet'
        db_table_comment = 'Master list of IHW discipline subnets'

    def __str__(self):
        return f"{self.subnet_name or self.subnet}"


class IhwFilepath(models.Model):
    """Directory paths for archive files (relative to /data/working/IHWv2/data/)"""
    dirpath = models.CharField(
        unique=True, 
        max_length=512, 
        db_comment='Directory path relative to archive root, no leading or trailing slash'
    )

    class Meta:
        managed = False
        db_table = 'ihw_filepath'
        db_table_comment = 'Directory paths for archive files (relative to configured root)'

    def __str__(self):
        return self.dirpath


class IhwFiles(models.Model):
    """Unique archive files identified by MD5 digest"""
    fileid = models.AutoField(primary_key=True)
    filename = models.CharField(max_length=64)
    subnet = models.ForeignKey(IhwSubnet, models.DO_NOTHING)
    type = models.CharField(max_length=16)
    arch_ver = models.CharField(max_length=8)
    digest = models.CharField(unique=True, max_length=32, db_comment='MD5 hash for deduplication')
    filesize = models.BigIntegerField(db_comment='File size in bytes')

    class Meta:
        managed = False
        db_table = 'ihw_files'
        db_table_comment = 'Master list of unique archive files, identified by MD5 digest'

    def __str__(self):
        return self.filename

    def get_file_paths(self):
        """Return all directory paths where this file exists"""
        return IhwFilepath.objects.filter(
            ihwfilefilepath__fileid=self
        ).distinct()

    def get_primary_path(self):
        """Return first available path for download"""
        paths = self.get_file_paths()
        return paths.first() if paths.exists() else None

    def get_full_path(self):
        """Construct full filesystem path for download"""
        primary_path = self.get_primary_path()
        if primary_path:
            return f"/data/working/IHWv2/data/{primary_path.dirpath}/{self.filename}"
        return None


class IhwFileFilepath(models.Model):
    """Junction table linking files to their directory locations"""
    fileid = models.ForeignKey(IhwFiles, models.DO_NOTHING, db_column='fileid')
    filepathid = models.ForeignKey(IhwFilepath, models.DO_NOTHING, db_column='filepathid')

    class Meta:
        managed = False
        db_table = 'ihw_file_filepath'
        unique_together = (('fileid', 'filepathid'),)
        db_table_comment = 'Utility link table between files and file paths'


class IhwEphemeris(models.Model):
    """Comet ephemeris data for position and solar distance"""
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

    def __str__(self):
        return f"{self.comet} @ {self.date} {self.hour or 0:.1f}h"

    @classmethod
    def for_date(cls, date_obs):
        """
        Find closest ephemeris entry for a given observation datetime
        Uses simple date match for now (can be optimized later)
        """
        obs_date = date_obs.date() if hasattr(date_obs, 'date') else date_obs
        return cls.objects.filter(date=obs_date, comet='Halley').first()


class IdxMetaCommon(models.Model):
    """Central hub for ALL observations across all networks"""
    network = models.ForeignKey(
        IhwNetwork, 
        models.DO_NOTHING, 
        db_comment='FK to ihw_network.id'
    )
    date_obs = models.DateTimeField(db_comment='UTC observation datetime')
    net_num = models.IntegerField(db_comment='Discipline-specific observation identifier')
    syscode = models.CharField(max_length=8, db_comment='IHW system code from FITS SYSTEM')
    observer = models.CharField(max_length=64)
    note_flag = models.IntegerField(db_comment='1 if notes are present')
    note = models.TextField(blank=True, null=True)
    object = models.CharField(max_length=24)
    idxfileid = models.ForeignKey(
        IhwFiles, 
        models.DO_NOTHING, 
        db_column='idxfileid', 
        blank=True, 
        null=True, 
        db_comment='FK to ihw_files.fileid (NULL if no data file)'
    )
    linenum = models.IntegerField(db_comment='Line number within source file')

    class Meta:
        managed = False
        db_table = 'idx_meta_common'
        unique_together = (('network', 'idxfileid', 'linenum'),)
        db_table_comment = 'Cross-discipline common metadata for all IHW networks'
        ordering = ['-date_obs']

    def __str__(self):
        return f"{self.date_obs.strftime('%Y-%m-%d %H:%M')} - {self.network.discipline} - {self.observer}"

    def get_absolute_url(self):
        return reverse('observation-detail', kwargs={'pk': self.pk})

    def get_ephemeris(self):
        """Get ephemeris data for this observation date"""
        return IhwEphemeris.for_date(self.date_obs)

    def get_position_display(self):
        """Return formatted RA/Dec from ephemeris if available"""
        ephem = self.get_ephemeris()
        if ephem and ephem.ra is not None and ephem.decl is not None:
            return f"RA: {ephem.ra:.4f}°, Dec: {ephem.decl:.4f}°"
        return "Position not available"

    def get_solar_distance_display(self):
        """Return formatted solar distance from ephemeris"""
        ephem = self.get_ephemeris()
        if ephem and ephem.r is not None:
            return f"{ephem.r:.3f} AU"
        return "N/A"

    def has_file(self):
        """Check if observation has associated data file"""
        return self.idxfileid is not None
