"""
IHW Core Models - International Halley Watch Archive
Generated from existing MariaDB schema - DO NOT MIGRATE
All models have managed=False to preserve legacy database
"""
from django.db import models
from django.urls import reverse
from django.conf import settings
import os


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

    def get_relative_path(self):
        """Construct relative path (without archive root) for display"""
        primary_path = self.get_primary_path()
        if primary_path:
            return f"{primary_path.dirpath}/{self.filename}"
        return None

    def get_full_path(self):
        """Construct full filesystem path for file operations"""
        from django.conf import settings
        relative_path = self.get_relative_path()
        if relative_path:
            return f"{settings.IHW_ARCHIVE_ROOT}{relative_path}"
        return None


class IhwFileFilepath(models.Model):
    """Junction table linking files to their directory locations"""
    fileid = models.ForeignKey(IhwFiles, models.DO_NOTHING, db_column='fileid', primary_key=True)
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


# ============================================================================
# Discipline-Specific Metadata Models
# ============================================================================
# Each idx_meta_* table contains specialized metadata for observations
# from a specific network/subnet. All link to IdxMetaCommon via meta_common_id
# ============================================================================

class IdxMetaAmdr(models.Model):
    """Amateur Drawing Network metadata"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    scale = models.DecimalField(max_digits=7, decimal_places=4, blank=True, null=True)
    aperture = models.DecimalField(max_digits=7, decimal_places=4, blank=True, null=True)
    instrument = models.CharField(max_length=4, blank=True, null=True)
    fratio = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    power_1 = models.SmallIntegerField(blank=True, null=True)
    power_2 = models.SmallIntegerField(blank=True, null=True)
    power_3 = models.SmallIntegerField(blank=True, null=True)
    duration = models.SmallIntegerField(blank=True, null=True)
    lim_magn = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    obs_site_id = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_amdr'


class IdxMetaAmpg(models.Model):
    """Amateur Photography Network metadata"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    foc_len = models.DecimalField(max_digits=7, decimal_places=4, blank=True, null=True)
    fratio = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    duration = models.SmallIntegerField(blank=True, null=True)
    emulsion = models.CharField(max_length=64, blank=True, null=True)
    filter_name = models.CharField(max_length=64, blank=True, null=True)
    hypersens = models.CharField(max_length=1, blank=True, null=True)
    aperture = models.DecimalField(max_digits=7, decimal_places=4, blank=True, null=True)
    dev_tech = models.CharField(max_length=64, blank=True, null=True)
    guiding = models.CharField(max_length=1, blank=True, null=True)
    lim_magn = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    image_qual = models.CharField(max_length=1, blank=True, null=True)
    obs_site_id = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_ampg'


class IdxMetaAmsp(models.Model):
    """Amateur Spectroscopy Network metadata"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    spectral_range_lo = models.FloatField(blank=True, null=True)
    spectral_range_hi = models.FloatField(blank=True, null=True)
    resolution = models.FloatField(blank=True, null=True)
    aperture = models.FloatField(blank=True, null=True)
    focal_len = models.FloatField(blank=True, null=True)
    dispersion = models.FloatField(blank=True, null=True)
    duration = models.SmallIntegerField(blank=True, null=True)
    emulsion = models.CharField(max_length=64, blank=True, null=True)
    hypersens = models.CharField(max_length=1, blank=True, null=True)
    dev_tech = models.CharField(max_length=64, blank=True, null=True)
    guiding = models.CharField(max_length=1, blank=True, null=True)
    lim_magn = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    image_qual = models.CharField(max_length=1, blank=True, null=True)
    obs_site_id = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_amsp'


class IdxMetaAmvis(models.Model):
    """Amateur Visual Observations (AMV/AMVIS) Network metadata"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    mag_gt = models.CharField(max_length=1, blank=True, null=True)
    magnitude = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    mag_comment = models.CharField(max_length=1, blank=True, null=True)
    mag_est_method = models.CharField(max_length=1, blank=True, null=True)
    chart = models.CharField(max_length=8, blank=True, null=True)
    coma_maj = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)
    coma_min = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)
    degree_cond = models.SmallIntegerField(blank=True, null=True)
    tail_len = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    tail_pos_ang = models.SmallIntegerField(blank=True, null=True)
    aperture = models.DecimalField(max_digits=7, decimal_places=4, blank=True, null=True)
    instrument = models.CharField(max_length=4, blank=True, null=True)
    fratio = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    power = models.SmallIntegerField(blank=True, null=True)
    lim_mag = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    lim_mag_comment = models.CharField(max_length=5, blank=True, null=True)
    dark_adapt = models.CharField(max_length=1, blank=True, null=True)
    obs_site_id = models.SmallIntegerField(blank=True, null=True)
    elevation = models.SmallIntegerField(blank=True, null=True)
    special_event_flag = models.CharField(max_length=1, blank=True, null=True)
    instrument_full = models.CharField(max_length=14, blank=True, null=True)
    tail_len_2 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    tail_pos_ang_2 = models.SmallIntegerField(blank=True, null=True)
    tail_len_3 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    tail_pos_ang_3 = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_amvis'


class IdxMetaAstrom(models.Model):
    """Astrometry Network metadata - astrometric measurements of comet position"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    
    # Julian date
    jd = models.FloatField()
    
    # Reported coordinates (as submitted)
    ra_reported = models.FloatField()
    dec_reported = models.FloatField()
    
    # Reduced coordinates (corrected/refined)
    ra = models.FloatField()
    decl = models.FloatField()
    
    # Quality and uncertainty
    acceptance_flag = models.CharField(max_length=1, blank=True, null=True)
    image_quality = models.CharField(max_length=1, blank=True, null=True)
    ra_rms = models.FloatField()
    dec_rms = models.FloatField()
    utc_corr = models.FloatField(blank=True, null=True)
    
    # Observatory location
    lon_obs = models.FloatField()
    lat_obs = models.FloatField()
    lat_calc_flag = models.CharField(max_length=1, blank=True, null=True)
    
    # Position offsets (from nucleus?)
    dxy = models.SmallIntegerField(blank=True, null=True)
    dz = models.SmallIntegerField(blank=True, null=True)
    
    # Magnitude measurements
    mag_total = models.FloatField(blank=True, null=True)
    mag_nucleus = models.FloatField(blank=True, null=True)
    
    # Observer information
    filenum = models.IntegerField(blank=True, null=True)
    obs_code = models.CharField(max_length=3)
    observer = models.CharField(max_length=24)
    observatory_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_astrom'


class IdxMetaIrim(models.Model):
    """Infrared Imaging Network metadata"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    lambda_eff = models.FloatField(blank=True, null=True)
    bandwidth = models.FloatField(blank=True, null=True)
    aperture = models.FloatField(blank=True, null=True)
    syscode = models.CharField(max_length=12, blank=True, null=True)
    observatory_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_irim'


class IdxMetaIrph(models.Model):
    """Infrared Photometry Network metadata"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    lambda_eff = models.FloatField(blank=True, null=True)
    bandwidth = models.FloatField(blank=True, null=True)
    aperture = models.FloatField(blank=True, null=True)
    syscode = models.CharField(max_length=12, blank=True, null=True)
    observatory_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_irph'


class IdxMetaIrpol(models.Model):
    """Infrared Polarimetry Network metadata"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    lambda_eff = models.FloatField(blank=True, null=True)
    bandwidth = models.FloatField(blank=True, null=True)
    aperture = models.FloatField(blank=True, null=True)
    syscode = models.CharField(max_length=12, blank=True, null=True)
    observatory_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_irpol'


class IdxMetaIrsp(models.Model):
    """Infrared Spectroscopy Network metadata"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    spectral_range_lo = models.FloatField(blank=True, null=True)
    spectral_range_hi = models.FloatField(blank=True, null=True)
    resolution = models.FloatField(blank=True, null=True)
    aperture = models.FloatField(blank=True, null=True)
    syscode = models.CharField(max_length=12, blank=True, null=True)
    observatory_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_irsp'


class IdxMetaLspn(models.Model):
    """Large-Scale Phenomena Network metadata (extensive FITS metadata)"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    
    # Observer and instrument details
    observer = models.CharField(max_length=64, blank=True, null=True)
    emulsion = models.CharField(max_length=25, blank=True, null=True)
    filter_name = models.CharField(max_length=25, blank=True, null=True)
    filterid = models.CharField(max_length=8, blank=True, null=True)
    exposure = models.FloatField(blank=True, null=True)
    calibration_flag = models.CharField(max_length=1, blank=True, null=True)
    data_quality = models.CharField(max_length=20, blank=True, null=True)
    observatory_id = models.IntegerField(blank=True, null=True)
    
    # Telescope/Instrument parameters
    aperture = models.FloatField(blank=True, null=True)
    fratio = models.FloatField(blank=True, null=True)
    detector = models.CharField(max_length=32, blank=True, null=True)
    cameraid = models.CharField(max_length=16, blank=True, null=True)
    chip_id = models.CharField(max_length=32, blank=True, null=True)
    instrume = models.CharField(max_length=16, blank=True, null=True)
    hypsen = models.CharField(max_length=1, blank=True, null=True)
    
    # Observatory location
    lat_obs = models.CharField(max_length=16, blank=True, null=True)
    long_obs = models.CharField(max_length=16, blank=True, null=True)
    elev_obs = models.SmallIntegerField(blank=True, null=True)
    
    # Observation conditions
    airm_mid = models.FloatField(blank=True, null=True)
    apsize = models.FloatField(blank=True, null=True)
    
    # Field of view
    fov_x = models.FloatField(blank=True, null=True)
    fov_y = models.FloatField(blank=True, null=True)
    
    # FITS image array metadata
    naxis = models.SmallIntegerField(blank=True, null=True)
    naxis1 = models.IntegerField(blank=True, null=True)
    naxis2 = models.IntegerField(blank=True, null=True)
    bitpix = models.SmallIntegerField(blank=True, null=True)
    bscale = models.FloatField(blank=True, null=True)
    bzero = models.FloatField(blank=True, null=True)
    blank = models.FloatField(blank=True, null=True)
    bunit = models.CharField(max_length=32, blank=True, null=True)
    
    # WCS (World Coordinate System) parameters
    cdelt1 = models.FloatField(blank=True, null=True)
    cdelt2 = models.FloatField(blank=True, null=True)
    crval1 = models.FloatField(blank=True, null=True)
    crval2 = models.FloatField(blank=True, null=True)
    crpix1 = models.FloatField(blank=True, null=True)
    crpix2 = models.FloatField(blank=True, null=True)
    crota1 = models.FloatField(blank=True, null=True)
    crota2 = models.FloatField(blank=True, null=True)
    ctype1 = models.CharField(max_length=16, blank=True, null=True)
    ctype2 = models.CharField(max_length=16, blank=True, null=True)
    equinox = models.FloatField(blank=True, null=True)
    
    # Coordinate headers
    ra_head = models.FloatField(blank=True, null=True)
    dec_head = models.FloatField(blank=True, null=True)
    ra_cpme = models.FloatField(blank=True, null=True)
    dec_cpme = models.FloatField(blank=True, null=True)
    
    # Plate/scan parameters
    pltscale = models.FloatField(blank=True, null=True)
    pltsze1 = models.FloatField(blank=True, null=True)
    pltsze2 = models.FloatField(blank=True, null=True)
    pltype = models.CharField(max_length=1, blank=True, null=True)
    scnstpx = models.SmallIntegerField(blank=True, null=True)
    scnstpy = models.SmallIntegerField(blank=True, null=True)
    scnstep = models.SmallIntegerField(blank=True, null=True)
    scnstp = models.SmallIntegerField(blank=True, null=True)
    scnapr = models.SmallIntegerField(blank=True, null=True)
    
    # Image dimensions and origin
    size = models.CharField(max_length=16, blank=True, null=True)
    maxcol = models.SmallIntegerField(blank=True, null=True)
    maxrow = models.SmallIntegerField(blank=True, null=True)
    orgcol = models.SmallIntegerField(blank=True, null=True)
    orgrow = models.SmallIntegerField(blank=True, null=True)
    
    # Calibration parameters
    ncalspot = models.SmallIntegerField(blank=True, null=True)
    ncalwdge = models.SmallIntegerField(blank=True, null=True)
    cometmax = models.FloatField(blank=True, null=True)
    skyden = models.SmallIntegerField(blank=True, null=True)
    skymin = models.FloatField(blank=True, null=True)
    skyunf = models.CharField(max_length=8, blank=True, null=True)
    sense = models.CharField(max_length=1, blank=True, null=True)
    
    # Data format and type
    dat_form = models.CharField(max_length=16, blank=True, null=True)
    dat_type = models.CharField(max_length=16, blank=True, null=True)
    
    # Processing dates
    date_pds = models.CharField(max_length=8, blank=True, null=True)
    date_prc = models.CharField(max_length=8, blank=True, null=True)
    date_rec = models.CharField(max_length=8, blank=True, null=True)
    date_rel = models.CharField(max_length=8, blank=True, null=True)
    date_wrt = models.CharField(max_length=8, blank=True, null=True)
    
    # Comments
    cmts_anl = models.CharField(max_length=80, blank=True, null=True)
    cmts_log = models.CharField(max_length=80, blank=True, null=True)
    cmts_obs = models.CharField(max_length=80, blank=True, null=True)
    cmts_prc = models.CharField(max_length=80, blank=True, null=True)
    cmts_log_alt = models.CharField(max_length=80, blank=True, null=True)
    log_cmts = models.CharField(max_length=80, blank=True, null=True)
    obs_cmts = models.CharField(max_length=80, blank=True, null=True)
    
    # Origin and submitter
    origin = models.CharField(max_length=32, blank=True, null=True)
    orging = models.CharField(max_length=32, blank=True, null=True)
    submittr = models.CharField(max_length=16, blank=True, null=True)
    
    # Miscellaneous
    file_num = models.IntegerField(blank=True, null=True)
    obslog = models.CharField(max_length=20, blank=True, null=True)
    spec_evt = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_lspn'


class IdxMetaMsnrdr(models.Model):
    """Meteor Studies Network RDR (Radar) metadata - meteor altitude/duration distributions"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    
    # Shower identification
    shower = models.CharField(max_length=20, blank=True, null=True)
    system = models.CharField(max_length=8, blank=True, null=True)
    limit_sensitiv = models.CharField(max_length=22, blank=True, null=True)
    direction = models.CharField(max_length=1, blank=True, null=True)
    
    # Meteor counts
    total_count = models.SmallIntegerField(blank=True, null=True)
    rads_count = models.SmallIntegerField(blank=True, null=True)
    
    # Duration bins
    dur_lt_h = models.SmallIntegerField(blank=True, null=True)
    dur_gt_h = models.SmallIntegerField(blank=True, null=True)
    dur_ge_1 = models.SmallIntegerField(blank=True, null=True)
    dur_gt_1 = models.FloatField(blank=True, null=True)
    dur_ge_8 = models.SmallIntegerField(blank=True, null=True)
    dur_gt_8 = models.FloatField(blank=True, null=True)
    net_time_count = models.FloatField(blank=True, null=True)
    
    # Altitude bins (70-350km in 10km increments, plus special ranges)
    alt_70_80km = models.SmallIntegerField(blank=True, null=True)
    alt_75_100km = models.SmallIntegerField(blank=True, null=True)
    alt_lt_90km = models.SmallIntegerField(blank=True, null=True)
    alt_80_90km = models.SmallIntegerField(blank=True, null=True)
    alt_90_100km = models.SmallIntegerField(blank=True, null=True)
    alt_100_110km = models.SmallIntegerField(blank=True, null=True)
    alt_110_120km = models.SmallIntegerField(blank=True, null=True)
    alt_120_130km = models.SmallIntegerField(blank=True, null=True)
    alt_130_140km = models.SmallIntegerField(blank=True, null=True)
    alt_140_150km = models.SmallIntegerField(blank=True, null=True)
    alt_150_160km = models.SmallIntegerField(blank=True, null=True)
    alt_160_170km = models.SmallIntegerField(blank=True, null=True)
    alt_170_180km = models.SmallIntegerField(blank=True, null=True)
    alt_180_190km = models.SmallIntegerField(blank=True, null=True)
    alt_190_200km = models.SmallIntegerField(blank=True, null=True)
    alt_200_210km = models.SmallIntegerField(blank=True, null=True)
    alt_210_220km = models.SmallIntegerField(blank=True, null=True)
    alt_201_225km = models.SmallIntegerField(blank=True, null=True)
    alt_220_230km = models.SmallIntegerField(blank=True, null=True)
    alt_230_240km = models.SmallIntegerField(blank=True, null=True)
    alt_226_250km = models.SmallIntegerField(blank=True, null=True)
    alt_240_250km = models.SmallIntegerField(blank=True, null=True)
    alt_250_260km = models.SmallIntegerField(blank=True, null=True)
    alt_260_270km = models.SmallIntegerField(blank=True, null=True)
    alt_270_280km = models.SmallIntegerField(blank=True, null=True)
    alt_280_290km = models.SmallIntegerField(blank=True, null=True)
    alt_290_300km = models.SmallIntegerField(blank=True, null=True)
    alt_noname = models.SmallIntegerField(blank=True, null=True)
    alt_gt_250km = models.SmallIntegerField(blank=True, null=True)
    alt_300_310km = models.SmallIntegerField(blank=True, null=True)
    alt_310_320km = models.SmallIntegerField(blank=True, null=True)
    alt_320_330km = models.SmallIntegerField(blank=True, null=True)
    alt_330_340km = models.SmallIntegerField(blank=True, null=True)
    alt_340_350km = models.SmallIntegerField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'idx_meta_msnrdr'


class IdxMetaMsnvis(models.Model):
    """Meteor Studies Network Visual metadata"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    # Minimal metadata for meteor visual observations
    
    class Meta:
        managed = False
        db_table = 'idx_meta_msnvis'


class IdxMetaNnsn(models.Model):
    """Near-Nucleus Studies Network metadata - high-resolution nuclear imaging"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    
    # Basic observation parameters
    filter_name = models.CharField(max_length=25, blank=True, null=True)
    exposure = models.FloatField(blank=True, null=True)
    airmass = models.FloatField(blank=True, null=True)
    data_quality = models.CharField(max_length=10, blank=True, null=True)
    observatory_id = models.IntegerField(blank=True, null=True)
    
    # Image metadata
    image_lines = models.SmallIntegerField(blank=True, null=True)
    image_samples = models.SmallIntegerField(blank=True, null=True)
    pixel_scale = models.FloatField(blank=True, null=True)
    flux_unit = models.CharField(max_length=20, blank=True, null=True)
    
    # Telescope parameters
    airm_mid = models.FloatField(blank=True, null=True)
    aperture = models.FloatField(blank=True, null=True)
    apsize = models.FloatField(blank=True, null=True)
    telefl = models.FloatField(blank=True, null=True)
    
    # FITS metadata
    bitpix = models.SmallIntegerField(blank=True, null=True)
    bunit = models.CharField(max_length=64, blank=True, null=True)
    naxis = models.SmallIntegerField(blank=True, null=True)
    
    # Image calibration/statistics
    cometmax = models.IntegerField(blank=True, null=True)
    skymin = models.IntegerField(blank=True, null=True)
    
    # WCS and data format
    crota1 = models.CharField(max_length=16, blank=True, null=True)
    dat_form = models.CharField(max_length=16, blank=True, null=True)
    sense = models.CharField(max_length=3, blank=True, null=True)
    
    # Observatory location
    elev_obs = models.SmallIntegerField(blank=True, null=True)
    
    # Processing metadata
    date_rel = models.CharField(max_length=8, blank=True, null=True)
    date_wrt = models.CharField(max_length=8, blank=True, null=True)
    origin = models.CharField(max_length=32, blank=True, null=True)
    submittr = models.CharField(max_length=24, blank=True, null=True)
    
    # Special event flag
    spec_evt = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_nnsn'


class IdxMetaPflx(models.Model):
    """Photometry Flux Network metadata"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    lambda_eff = models.FloatField(blank=True, null=True)
    bandwidth = models.FloatField(blank=True, null=True)
    aperture = models.FloatField(blank=True, null=True)
    syscode = models.CharField(max_length=12, blank=True, null=True)
    observatory_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_pflx'


class IdxMetaPmag(models.Model):
    """Photometry Magnitude Network metadata"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    lambda_eff = models.FloatField(blank=True, null=True)
    bandwidth = models.FloatField(blank=True, null=True)
    aperture = models.FloatField(blank=True, null=True)
    syscode = models.CharField(max_length=12, blank=True, null=True)
    observatory_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_pmag'


class IdxMetaPpol(models.Model):
    """Photometry Polarimetry Network metadata"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    lambda_eff = models.FloatField(blank=True, null=True)
    bandwidth = models.FloatField(blank=True, null=True)
    aperture = models.FloatField(blank=True, null=True)
    syscode = models.CharField(max_length=12, blank=True, null=True)
    observatory_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_ppol'


class IdxMetaPsto(models.Model):
    """Photometry Stokes Network metadata"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    lambda_eff = models.FloatField(blank=True, null=True)
    bandwidth = models.FloatField(blank=True, null=True)
    aperture = models.FloatField(blank=True, null=True)
    syscode = models.CharField(max_length=12, blank=True, null=True)
    observatory_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_psto'


class IdxMetaRscn(models.Model):
    """Radio Science Continuum Network metadata"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    image_lines = models.IntegerField(blank=True, null=True)
    image_samples = models.IntegerField(blank=True, null=True)
    scaling_factor = models.FloatField(blank=True, null=True)
    offset_val = models.FloatField(blank=True, null=True)
    cent_freq = models.FloatField(blank=True, null=True)
    bandwidth = models.FloatField(blank=True, null=True)
    beamsize = models.FloatField(blank=True, null=True)
    beam_elong = models.FloatField(blank=True, null=True)
    beam_rotation = models.FloatField(blank=True, null=True)
    dat_type = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_rscn'


class IdxMetaRsoc(models.Model):
    """Radio Science Occultation Network metadata"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    image_lines = models.IntegerField(blank=True, null=True)
    image_samples = models.IntegerField(blank=True, null=True)
    scaling_factor = models.FloatField(blank=True, null=True)
    offset_val = models.FloatField(blank=True, null=True)
    derived_max = models.FloatField(blank=True, null=True)
    derived_min = models.FloatField(blank=True, null=True)
    cent_freq = models.FloatField(blank=True, null=True)
    bandwidth = models.FloatField(blank=True, null=True)
    beamsize = models.FloatField(blank=True, null=True)
    beam_elong = models.FloatField(blank=True, null=True)
    beam_rotation = models.FloatField(blank=True, null=True)
    dat_type = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_rsoc'


class IdxMetaRsoh(models.Model):
    """Radio Science OH Line Network metadata"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    spectrum_rows = models.IntegerField(blank=True, null=True)
    scaling_factor = models.FloatField(blank=True, null=True)
    offset_val = models.FloatField(blank=True, null=True)
    derived_max = models.FloatField(blank=True, null=True)
    derived_min = models.FloatField(blank=True, null=True)
    velo_min = models.FloatField(blank=True, null=True)
    velo_interval = models.FloatField(blank=True, null=True)
    cent_freq = models.FloatField(blank=True, null=True)
    bandwidth = models.FloatField(blank=True, null=True)
    beamsize = models.FloatField(blank=True, null=True)
    beam_elong = models.FloatField(blank=True, null=True)
    beam_rotation = models.FloatField(blank=True, null=True)
    dat_type = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_rsoh'


class IdxMetaRsrdr(models.Model):
    """Radio Science RDR Network metadata"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    rhc_rows = models.IntegerField(blank=True, null=True)
    rhc_scaling_factor = models.FloatField(blank=True, null=True)
    rhc_offset = models.FloatField(blank=True, null=True)
    rhc_freq_min = models.FloatField(blank=True, null=True)
    rhc_freq_interval = models.FloatField(blank=True, null=True)
    rhc_derived_max = models.FloatField(blank=True, null=True)
    rhc_derived_min = models.FloatField(blank=True, null=True)
    lhc_rows = models.IntegerField(blank=True, null=True)
    lhc_scaling_factor = models.FloatField(blank=True, null=True)
    lhc_offset = models.FloatField(blank=True, null=True)
    lhc_freq_min = models.FloatField(blank=True, null=True)
    lhc_freq_interval = models.FloatField(blank=True, null=True)
    lhc_derived_max = models.FloatField(blank=True, null=True)
    lhc_derived_min = models.FloatField(blank=True, null=True)
    cent_freq = models.FloatField(blank=True, null=True)
    bandwidth = models.FloatField(blank=True, null=True)
    dat_type = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_rsrdr'


class IdxMetaRssl(models.Model):
    """Radio Science Spectral Line Network metadata"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    spectrum_rows = models.IntegerField(blank=True, null=True)
    scaling_factor = models.FloatField(blank=True, null=True)
    offset_val = models.FloatField(blank=True, null=True)
    derived_max = models.FloatField(blank=True, null=True)
    derived_min = models.FloatField(blank=True, null=True)
    velo_min = models.FloatField(blank=True, null=True)
    velo_interval = models.FloatField(blank=True, null=True)
    cent_freq = models.FloatField(blank=True, null=True)
    bandwidth = models.FloatField(blank=True, null=True)
    beamsize = models.FloatField(blank=True, null=True)
    beam_elong = models.FloatField(blank=True, null=True)
    beam_rotation = models.FloatField(blank=True, null=True)
    dat_type = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_rssl'


class IdxMetaRsuv(models.Model):
    """Radio Science UV Network metadata"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    spectrum_rows = models.IntegerField(blank=True, null=True)
    spectrum_cols = models.IntegerField(blank=True, null=True)
    freq_min = models.FloatField(blank=True, null=True)
    freq_interval = models.FloatField(blank=True, null=True)
    scaling_factor = models.FloatField(blank=True, null=True)
    cent_freq = models.FloatField(blank=True, null=True)
    bandwidth = models.FloatField(blank=True, null=True)
    dat_type = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_rsuv'


class IdxMetaSpectra(models.Model):
    """Spectroscopy Network metadata - spectroscopic observations"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    
    # SSN identifier
    ssn_num = models.IntegerField(blank=True, null=True)
    
    # Data format and type
    dat_form = models.CharField(max_length=10, blank=True, null=True)
    dat_type = models.CharField(max_length=20, blank=True, null=True)
    dis_code = models.CharField(max_length=12, blank=True, null=True)
    calibration = models.CharField(max_length=1, blank=True, null=True)
    
    # Spectral characteristics
    resolution = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    range_lo = models.IntegerField(blank=True, null=True)
    range_hi = models.IntegerField(blank=True, null=True)
    
    # Observation parameters
    exposure = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    aperture = models.CharField(max_length=80, blank=True, null=True)
    slit_size = models.CharField(max_length=10, blank=True, null=True)
    slit_pa = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)
    airmass = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    elevation = models.DecimalField(max_digits=7, decimal_places=1, blank=True, null=True)
    
    # Data dimensions
    axes = models.SmallIntegerField(blank=True, null=True)
    axis_1 = models.SmallIntegerField(blank=True, null=True)
    axis_2 = models.SmallIntegerField(blank=True, null=True)
    
    # Offset from nucleus
    separ_nucl = models.DecimalField(max_digits=8, decimal_places=1, blank=True, null=True)
    offset_rho = models.DecimalField(max_digits=8, decimal_places=1, blank=True, null=True)
    offset_theta = models.SmallIntegerField(blank=True, null=True)
    
    # Quality
    quality = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_spectra'


# ============================================================================
# Helper Functions
# ============================================================================

def get_discipline_metadata_model(observation):
    """
    Get the discipline-specific metadata model class for an observation.
    
    Args:
        observation: IdxMetaCommon instance
        
    Returns:
        Model class or None if no metadata table exists for this discipline
    """
    # Map subnet codes to model classes
    SUBNET_TO_MODEL = {
        'AMDR': IdxMetaAmdr,
        'AMPG': IdxMetaAmpg,
        'AMSP': IdxMetaAmsp,
        'AMV': IdxMetaAmvis,
        'AMVIS': IdxMetaAmvis,  # Alternative name for AMV
        'ASTROM': IdxMetaAstrom,
        'IRIM': IdxMetaIrim,
        'IRPH': IdxMetaIrph,
        'IRPOL': IdxMetaIrpol,
        'IRSP': IdxMetaIrsp,
        'LSPN': IdxMetaLspn,
        'MSNRDR': IdxMetaMsnrdr,
        'MSNVIS': IdxMetaMsnvis,
        'NNSN': IdxMetaNnsn,
        'PFLX': IdxMetaPflx,
        'PMAG': IdxMetaPmag,
        'PPOL': IdxMetaPpol,
        'PSTO': IdxMetaPsto,
        'RSCN': IdxMetaRscn,
        'RSOC': IdxMetaRsoc,
        'RSOH': IdxMetaRsoh,
        'RSRDR': IdxMetaRsrdr,
        'RSSL': IdxMetaRssl,
        'RSUV': IdxMetaRsuv,
        'SPECTRA': IdxMetaSpectra,
    }
    
    # Get subnet from observation's file
    if observation.idxfileid and observation.idxfileid.subnet:
        subnet_code = observation.idxfileid.subnet.subnet.upper()
        return SUBNET_TO_MODEL.get(subnet_code)
    
    return None


def get_discipline_metadata(observation):
    """
    Fetch discipline-specific metadata for an observation.
    
    Args:
        observation: IdxMetaCommon instance
        
    Returns:
        Model instance or None if no metadata exists
    """
    model_class = get_discipline_metadata_model(observation)
    if model_class:
        try:
            return model_class.objects.get(meta_common=observation)
        except model_class.DoesNotExist:
            return None
    return None


def format_metadata_fields(metadata_obj):
    """
    Convert metadata object into formatted display dictionary.
    
    Args:
        metadata_obj: Discipline-specific metadata model instance
        
    Returns:
        List of (field_label, field_value) tuples for display
    """
    if not metadata_obj:
        return []
    
    # Skip these system/FK fields
    skip_fields = {'id', 'meta_common', 'meta_common_id'}
    
    # Field name formatting: snake_case to Title Case with units
    field_labels = {
        'spectral_range_lo': 'Spectral Range (Low)',
        'spectral_range_hi': 'Spectral Range (High)',
        'lambda_eff': 'Effective Wavelength (λ)',
        'mag_gt': 'Magnitude >',
        'mag_comment': 'Magnitude Comment',
        'mag_est_method': 'Magnitude Estimation Method',
        'coma_maj': 'Coma Major Axis',
        'coma_min': 'Coma Minor Axis',
        'degree_cond': 'Observing Conditions',
        'tail_len': 'Tail Length',
        'tail_pos_ang': 'Tail Position Angle',
        'lim_mag': 'Limiting Magnitude',
        'lim_mag_comment': 'Limiting Magnitude Comment',
        'dark_adapt': 'Dark Adapted',
        'obs_site_id': 'Observatory Site ID',
        'observatory_id': 'Observatory ID',
        'foc_len': 'Focal Length',
        'fratio': 'F-Ratio',
        'dev_tech': 'Development Technique',
        'image_qual': 'Image Quality',
        'lim_magn': 'Limiting Magnitude',
        'special_event_flag': 'Special Event',
        'instrument_full': 'Instrument',
        'ra': 'Right Ascension',
        'dec': 'Declination',
        'delta_ra': 'RA Error',
        'delta_dec': 'Dec Error',
        'delta_mag': 'Magnitude Error',
        'uncertainty_a': 'Uncertainty A',
        'uncertainty_b': 'Uncertainty B',
        'position_angle': 'Position Angle',
        'ref_cat': 'Reference Catalog',
        'fov_x': 'Field of View X',
        'fov_y': 'Field of View Y',
        'calibration_flag': 'Calibration',
        'data_quality': 'Data Quality',
        'airm_mid': 'Airmass (mid)',
        'naxis': 'Number of Axes',
        'naxis1': 'X-Axis Size',
        'naxis2': 'Y-Axis Size',
        'line_id': 'Spectral Line',
        # Radio Science Network fields
        'image_lines': 'Image Lines',
        'image_samples': 'Image Samples',
        'scaling_factor': 'Scaling Factor',
        'offset_val': 'Offset Value',
        'cent_freq': 'Center Frequency',
        'beamsize': 'Beam Size',
        'beam_elong': 'Beam Elongation',
        'beam_rotation': 'Beam Rotation',
        'dat_type': 'Data Type',
        'derived_max': 'Derived Maximum',
        'derived_min': 'Derived Minimum',
        'spectrum_rows': 'Spectrum Rows',
        'spectrum_cols': 'Spectrum Columns',
        'velo_min': 'Velocity Minimum',
        'velo_interval': 'Velocity Interval',
        'freq_min': 'Frequency Minimum',
        'freq_interval': 'Frequency Interval',
        # RHC/LHC polarization fields (RSRDR)
        'rhc_rows': 'RHC Rows',
        'rhc_scaling_factor': 'RHC Scaling Factor',
        'rhc_offset': 'RHC Offset',
        'rhc_freq_min': 'RHC Frequency Min',
        'rhc_freq_interval': 'RHC Frequency Interval',
        'rhc_derived_max': 'RHC Derived Max',
        'rhc_derived_min': 'RHC Derived Min',
        'lhc_rows': 'LHC Rows',
        'lhc_scaling_factor': 'LHC Scaling Factor',
        'lhc_offset': 'LHC Offset',
        'lhc_freq_min': 'LHC Frequency Min',
        'lhc_freq_interval': 'LHC Frequency Interval',
        'lhc_derived_max': 'LHC Derived Max',
        'lhc_derived_min': 'LHC Derived Min',
    }
    
    result = []
    for field in metadata_obj._meta.get_fields():
        if field.name in skip_fields:
            continue
            
        value = getattr(metadata_obj, field.name, None)
        if value is not None and value != '':
            # Format field name
            label = field_labels.get(field.name, field.name.replace('_', ' ').title())
            result.append((label, value))
    
    return result
