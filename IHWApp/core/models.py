"""
IHW Core Models - International Halley Watch Archive
Generated from existing MariaDB schema - DO NOT MIGRATE
All models have managed=False to preserve legacy database
"""
from django.db import models
from django.urls import reverse
from django.conf import settings
import os


class ApxIhwObscodes(models.Model):
    """IHW Observatory Codes - Observatory metadata and locations"""
    system = models.CharField(max_length=10)
    observatory = models.CharField(max_length=40)
    location = models.CharField(max_length=40, blank=True, null=True)
    instrument = models.CharField(max_length=60, blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    subdiscipline = models.IntegerField(blank=True, null=True)
    telescope = models.CharField(max_length=40, blank=True, null=True)
    aperture = models.FloatField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'apx_ihw_obscodes'
        db_table_comment = 'IHW Observatory codes and metadata'
    
    def __str__(self):
        if self.location:
            return f"{self.observatory} ({self.location})"
        return self.observatory


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
    
    # Telescope parameters
    foc_len = models.DecimalField(max_digits=7, decimal_places=4, blank=True, null=True)
    fratio = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    aperture = models.DecimalField(max_digits=7, decimal_places=4, blank=True, null=True)
    
    # Field of view
    fov1 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    fov2 = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    
    # Observation parameters
    duration = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    emulsion = models.CharField(max_length=14, blank=True, null=True)
    iso_din = models.CharField(max_length=8, blank=True, null=True)
    hypersense = models.CharField(max_length=1, blank=True, null=True)
    guiding = models.CharField(max_length=1, blank=True, null=True)
    
    # Identification
    idno = models.CharField(max_length=8, blank=True, null=True)
    obs_site_id = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_ampg'


class IdxMetaAmsp(models.Model):
    """Amateur Spectroscopy Network metadata"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    
    # Instrument configuration
    config = models.CharField(max_length=8, blank=True, null=True)
    instrument = models.CharField(max_length=4, blank=True, null=True)
    
    # Telescope parameters
    foc_len = models.DecimalField(max_digits=7, decimal_places=4, blank=True, null=True)
    fratio = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    aperture = models.DecimalField(max_digits=7, decimal_places=4, blank=True, null=True)
    
    # Observation parameters
    duration = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    emulsion = models.CharField(max_length=14, blank=True, null=True)
    iso = models.CharField(max_length=8, blank=True, null=True)
    hypsen = models.CharField(max_length=1, blank=True, null=True)
    guiding = models.CharField(max_length=1, blank=True, null=True)
    
    # Identification
    idno = models.CharField(max_length=8, blank=True, null=True)
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
    
    # Filter
    filter = models.CharField(max_length=10)
    
    # Image dimensions
    image_lines = models.SmallIntegerField(blank=True, null=True)
    image_samples = models.SmallIntegerField(blank=True, null=True)
    pixel_scale = models.FloatField(blank=True, null=True)
    
    # Flux units
    flux_unit = models.CharField(max_length=20, blank=True, null=True)
    
    # System identification
    syscode = models.CharField(max_length=12)
    observatory_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_irim'


class IdxMetaIrph(models.Model):
    """Infrared Photometry Network metadata"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    
    # Photometry type
    irphot_type = models.CharField(max_length=12)
    
    # System identification
    syscode = models.CharField(max_length=12)
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
    """Meteor Studies Network Visual metadata - visual meteor observations"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    
    # Shower identification
    shower = models.CharField(max_length=20, blank=True, null=True)
    
    # Observation site
    site_num = models.SmallIntegerField(blank=True, null=True)
    site_name = models.CharField(max_length=20, blank=True, null=True)
    
    # Observer information
    obs_num = models.SmallIntegerField(blank=True, null=True)
    observer_id = models.IntegerField(blank=True, null=True)
    
    # Meteor counts
    total_meteor_count = models.SmallIntegerField(blank=True, null=True)
    count_shower = models.SmallIntegerField(blank=True, null=True)
    count_noshower = models.SmallIntegerField(blank=True, null=True)
    
    # Observing conditions
    mag_limit = models.FloatField(blank=True, null=True)
    cloud_cover = models.SmallIntegerField(blank=True, null=True)
    
    # Source file references
    source_fileid = models.IntegerField(blank=True, null=True)
    source_filepathid = models.IntegerField(blank=True, null=True)
    
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
    """Photometry Flux Network metadata - flux measurements"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    
    # Filter/wavelength parameters
    filter_name = models.CharField(max_length=10, blank=True, null=True)
    center_wavelength = models.IntegerField(blank=True, null=True)
    bandpass = models.IntegerField(blank=True, null=True)
    
    # Flux measurement
    limit_flag = models.CharField(max_length=1, blank=True, null=True)
    log_flux = models.FloatField(blank=True, null=True)
    flux_error = models.FloatField(blank=True, null=True)
    
    # Observation parameters
    observing_aperture = models.FloatField(blank=True, null=True)
    telescope_aperture = models.FloatField(blank=True, null=True)
    integration_time = models.IntegerField(blank=True, null=True)
    airmass = models.FloatField(blank=True, null=True)
    
    # Offset from nucleus
    rho = models.IntegerField(blank=True, null=True)
    theta = models.IntegerField(blank=True, null=True)
    
    # Observatory and notes
    observatory_id = models.IntegerField(blank=True, null=True)
    note_code = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_pflx'


class IdxMetaPmag(models.Model):
    """Photometry Magnitude Network metadata - magnitude measurements"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    
    # PPN identifier
    ppn_num = models.IntegerField(blank=True, null=True)
    
    # Filter/wavelength parameters
    filter_name = models.CharField(max_length=4, blank=True, null=True)
    wavelength = models.SmallIntegerField(blank=True, null=True)
    bandpass = models.SmallIntegerField(blank=True, null=True)
    
    # Observation parameters
    aperture_diam = models.FloatField(blank=True, null=True)
    duration = models.SmallIntegerField(blank=True, null=True)
    airmass = models.FloatField(blank=True, null=True)
    
    # Magnitude measurement
    mag_lt = models.CharField(max_length=1, blank=True, null=True)
    magnitude = models.FloatField(blank=True, null=True)
    mag_error = models.FloatField(blank=True, null=True)
    
    # Offset from nucleus
    offset_rho = models.SmallIntegerField(blank=True, null=True)
    offset_theta = models.SmallIntegerField(blank=True, null=True)
    
    # Notes
    note_flag = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_pmag'


class IdxMetaPpol(models.Model):
    """Photometry Polarimetry Network metadata - polarization measurements"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    
    # PPN identifier
    ppn_num = models.IntegerField(blank=True, null=True)
    
    # Filter/wavelength parameters
    filter_name = models.CharField(max_length=4, blank=True, null=True)
    wavelength = models.SmallIntegerField(blank=True, null=True)
    bandpass = models.SmallIntegerField(blank=True, null=True)
    
    # Observation parameters
    aperture_diam = models.FloatField(blank=True, null=True)
    duration = models.SmallIntegerField(blank=True, null=True)
    airmass = models.FloatField(blank=True, null=True)
    
    # Polarization measurement
    polariz_type = models.CharField(max_length=2, blank=True, null=True)
    polarization = models.FloatField(blank=True, null=True)
    polariz_error = models.FloatField(blank=True, null=True)
    polariz_angle = models.FloatField(blank=True, null=True)
    polariz_angle_err = models.FloatField(blank=True, null=True)
    
    # Offset from nucleus
    offset_rho = models.SmallIntegerField(blank=True, null=True)
    offset_theta = models.SmallIntegerField(blank=True, null=True)
    
    # Notes
    note_flag = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idx_meta_ppol'


class IdxMetaPsto(models.Model):
    """Photometry Stokes Network metadata - Stokes parameter measurements"""
    meta_common = models.ForeignKey(IdxMetaCommon, models.DO_NOTHING, db_column='meta_common_id')
    
    # PPN identifier
    ppn_num = models.IntegerField(blank=True, null=True)
    
    # Filter/wavelength parameters
    filter_name = models.CharField(max_length=4, blank=True, null=True)
    wavelength = models.SmallIntegerField(blank=True, null=True)
    bandpass = models.SmallIntegerField(blank=True, null=True)
    
    # Observation parameters
    aperture_diam = models.FloatField(blank=True, null=True)
    duration = models.SmallIntegerField(blank=True, null=True)
    airmass = models.FloatField(blank=True, null=True)
    
    # Stokes parameters (Q/I, U/I, V/I)
    q_over_i = models.FloatField(blank=True, null=True)
    q_over_i_err = models.FloatField(blank=True, null=True)
    u_over_i = models.FloatField(blank=True, null=True)
    u_over_i_err = models.FloatField(blank=True, null=True)
    v_over_i = models.FloatField(blank=True, null=True)
    v_over_i_err = models.FloatField(blank=True, null=True)
    
    # Offset from nucleus
    offset_rho = models.SmallIntegerField(blank=True, null=True)
    offset_theta = models.SmallIntegerField(blank=True, null=True)
    
    # Notes
    note_flag = models.CharField(max_length=1, blank=True, null=True)

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


def get_comprehensive_field_labels():
    """
    Returns comprehensive field label mapping for all 334+ metadata fields.
    """
    return {
        # Common observation fields
        'observer': 'Observer',
        'syscode': 'System Code',
        'observatory_id': 'Observatory',
        
        # Instrument/Telescope parameters
        'instrument': 'Instrument',
        'instrume': 'Instrument Name',
        'config': 'Configuration',
        'aperture': 'Aperture (cm)',
        'fratio': 'F-Ratio',
        'foc_len': 'Focal Length (m)',
        'telefl': 'Telescope Focal Length',
        'detector': 'Detector',
        'cameraid': 'Camera ID',
        'chip_id': 'CCD Chip ID',
        
        # Observation parameters
        'exposure': 'Exposure Time (s)',
        'duration': 'Duration (s)',
        'integration_time': 'Integration Time (s)',
        'airmass': 'Airmass',
        'airm_mid': 'Airmass (midpoint)',
        'elevation': 'Elevation (deg)',
        'apsize': 'Aperture Size (arcsec)',
        'observing_aperture': 'Observing Aperture',
        'telescope_aperture': 'Telescope Aperture',
        'aperture_diam': 'Aperture Diameter',
        
        # Filter/wavelength
        'filter': 'Filter',
        'filter_name': 'Filter',
        'filterid': 'Filter ID',
        'emulsion': 'Film/Emulsion',
        'iso': 'ISO Speed',
        'iso_din': 'ISO/DIN Rating',
        'hypsen': 'Hypersensitized',
        'hypersense': 'Hypersensitized',
        'center_wavelength': 'Center Wavelength (Å)',
        'wavelength': 'Wavelength (Å)',
        'bandpass': 'Bandpass (Å)',
        'bandwidth': 'Bandwidth',
        
        # Field of view
        'fov_x': 'FOV Width (arcmin)',
        'fov_y': 'FOV Height (arcmin)',
        'fov1': 'FOV Dimension 1 (deg)',
        'fov2': 'FOV Dimension 2 (deg)',
        
        # Quality/flags
        'data_quality': 'Data Quality',
        'image_qual': 'Image Quality',
        'calibration': 'Calibration Status',
        'calibration_flag': 'Calibration Flag',
        'quality': 'Quality',
        'acceptance_flag': 'Acceptance Flag',
        'image_quality': 'Image Quality',
        'note_flag': 'Note Flag',
        'note_code': 'Note Code',
        'spec_evt': 'Special Event',
        
        # FITS image metadata
        'naxis': 'FITS: Number of Axes',
        'naxis1': 'FITS: Width (pixels)',
        'naxis2': 'FITS: Height (pixels)',
        'bitpix': 'FITS: Bits per Pixel',
        'bscale': 'FITS: Scaling Factor',
        'bzero': 'FITS: Zero Offset',
        'blank': 'FITS: Blank Value',
        'bunit': 'FITS: Brightness Unit',
        
        # WCS (World Coordinate System)
        'cdelt1': 'WCS: RA Pixel Scale (deg/pix)',
        'cdelt2': 'WCS: Dec Pixel Scale (deg/pix)',
        'crval1': 'WCS: RA Reference Value (deg)',
        'crval2': 'WCS: Dec Reference Value (deg)',
        'crpix1': 'WCS: Reference Pixel X',
        'crpix2': 'WCS: Reference Pixel Y',
        'crota1': 'WCS: Rotation Angle 1 (deg)',
        'crota2': 'WCS: Rotation Angle 2 (deg)',
        'ctype1': 'WCS: Coordinate Type 1',
        'ctype2': 'WCS: Coordinate Type 2',
        'equinox': 'WCS: Equinox',
        
        # Coordinates
        'ra': 'Right Ascension (deg)',
        'decl': 'Declination (deg)',
        'dec': 'Declination (deg)',
        'ra_reported': 'RA (reported)',
        'dec_reported': 'Dec (reported)',
        'ra_head': 'RA (header)',
        'dec_head': 'Dec (header)',
        'ra_cpme': 'RA (computed)',
        'dec_cpme': 'Dec (computed)',
        'ra_rms': 'RA RMS Error',
        'dec_rms': 'Dec RMS Error',
        'jd': 'Julian Date',
        'utc_corr': 'UTC Correction',
        
        # Observatory location
        'lat_obs': 'Observatory Latitude',
        'long_obs': 'Observatory Longitude',
        'lon_obs': 'Observatory Longitude',
        'elev_obs': 'Observatory Elevation (m)',
        'lat_calc_flag': 'Latitude Calculation Flag',
        
        # Offset from nucleus
        'offset_rho': 'Radial Offset (arcsec)',
        'offset_theta': 'Position Angle (deg)',
        'rho': 'Offset Distance',
        'theta': 'Position Angle',
        'separ_nucl': 'Nuclear Separation',
        'dxy': 'XY Offset',
        'dz': 'Z Offset',
        
        # Magnitude measurements
        'magnitude': 'Magnitude',
        'mag_total': 'Total Magnitude',
        'mag_nucleus': 'Nuclear Magnitude',
        'mag_error': 'Magnitude Error',
        'mag_lt': 'Magnitude Limit Flag',
        'lim_mag': 'Limiting Magnitude',
        'lim_magn': 'Limiting Magnitude',
        'mag_limit': 'Limiting Magnitude',
        
        # Flux/photometry
        'log_flux': 'Log Flux',
        'flux_error': 'Flux Error',
        'limit_flag': 'Limit Flag',
        'flux_unit': 'Flux Units',
        
        # Polarimetry
        'polarization': 'Polarization (%)',
        'polariz_error': 'Polarization Error',
        'polariz_angle': 'Polarization Angle (deg)',
        'polariz_angle_err': 'Pol. Angle Error',
        'polariz_type': 'Polarization Type',
        
        # Stokes parameters
        'q_over_i': 'Q/I',
        'q_over_i_err': 'Q/I Error',
        'u_over_i': 'U/I',
        'u_over_i_err': 'U/I Error',
        'v_over_i': 'V/I',
        'v_over_i_err': 'V/I Error',
        
        # Spectroscopy
        'ssn_num': 'SSN Number',
        'resolution': 'Spectral Resolution',
        'resolut': 'Resolution',
        'res_unit': 'Resolution Unit',
        'res_code': 'Resolution Code',
        'range_lo': 'Wavelength Min (Å)',
        'range_hi': 'Wavelength Max (Å)',
        'spectral_range_lo': 'Spectral Range Min (Å)',
        'spectral_range_hi': 'Spectral Range Max (Å)',
        'slit_size': 'Slit Size',
        'slit_pa': 'Slit Position Angle (deg)',
        'slit_width': 'Slit Width',
        'slit_height': 'Slit Height',
        'dis_code': 'Dispersion Code',
        'axes': 'Number of Axes',
        'axis_1': 'Axis 1 Dimension',
        'axis_2': 'Axis 2 Dimension',
        'spectrum_notes': 'Spectrum Notes',
        
        # Astrometry
        'obs_code': 'Observatory Code',
        'filenum': 'File Number',
        'nref': 'Number of Reference Stars',
        'npos': 'Number of Positions',
        'ref_cat': 'Reference Catalog',
        'method': 'Reduction Method',
        'rmsa': 'RMS RA',
        'rmsd': 'RMS Dec',
        'uncertainty_a': 'Uncertainty Semi-major (arcsec)',
        'uncertainty_b': 'Uncertainty Semi-minor (arcsec)',
        'position_angle': 'Position Angle (deg)',
        
        # Plate/scan parameters
        'pltscale': 'Plate Scale (arcsec/mm)',
        'pltsze1': 'Plate Size 1 (mm)',
        'pltsze2': 'Plate Size 2 (mm)',
        'pltype': 'Plate Type',
        'scnstpx': 'Scan Step X (μm)',
        'scnstpy': 'Scan Step Y (μm)',
        'scnstep': 'Scan Step (μm)',
        'scnstp': 'Scan Step',
        'scnapr': 'Scan Aperture',
        'pixel_scale': 'Pixel Scale (arcsec/pixel)',
        
        # Image dimensions
        'image_lines': 'Image Lines',
        'image_samples': 'Image Samples',
        'size': 'Image Size',
        'maxcol': 'Max Column',
        'maxrow': 'Max Row',
        'orgcol': 'Origin Column',
        'orgrow': 'Origin Row',
        
        # Calibration
        'ncalspot': 'N Calibration Spots',
        'ncalwdge': 'N Calibration Wedges',
        'cometmax': 'Comet Maximum (DN)',
        'skyden': 'Sky Density',
        'skymin': 'Sky Minimum',
        'skyunf': 'Sky Uniformity',
        'sense': 'Sensitivity',
        
        # Data format
        'dat_form': 'Data Format',
        'dat_type': 'Data Type',
        
        # Processing dates
        'date_pds': 'PDS Archive Date',
        'date_prc': 'Processing Date',
        'date_rec': 'Received Date',
        'date_rel': 'Release Date',
        'date_wrt': 'Written Date',
        
        # Comments (multiple types)
        'cmts_anl': 'Analysis Comments',
        'cmts_log': 'Log Comments',
        'cmts_obs': 'Observer Comments',
        'cmts_prc': 'Processing Comments',
        'cmts_log_alt': 'Alternate Log Comments',
        'log_cmts': 'Log Comments',
        'obs_cmts': 'Observer Comments',
        
        # Origin/submitter
        'origin': 'Origin',
        'orging': 'Original Ingestor',
        'submittr': 'Submitter',
        'file_num': 'File Number',
        'obslog': 'Observation Log',
        'obs_site_id': 'Observation Site ID',
        'ppn_num': 'PPN Number',
        'idno': 'ID Number',
        
        # Meteor-specific
        'shower': 'Meteor Shower',
        'system': 'Detection System',
        'limit_sensitiv': 'Sensitivity Limit',
        'direction': 'Direction',
        'total_count': 'Total Count',
        'rads_count': 'Radiant Count',
        'total_meteor_count': 'Total Meteor Count',
        'count_shower': 'Shower Meteors',
        'count_noshower': 'Sporadic Meteors',
        'cloud_cover': 'Cloud Cover',
        'site_num': 'Site Number',
        'site_name': 'Site Name',
        'obs_num': 'Observer Number',
        'observer_id': 'Observer ID',
        'source_fileid': 'Source File ID',
        'source_filepathid': 'Source Filepath ID',
        
        # Meteor duration bins
        'dur_lt_h': 'Duration < 0.5s',
        'dur_gt_h': 'Duration > 0.5s',
        'dur_ge_1': 'Duration ≥ 1s',
        'dur_gt_1': 'Duration > 1s',
        'dur_ge_8': 'Duration ≥ 8s',
        'dur_gt_8': 'Duration > 8s',
        'net_time_count': 'Net Time Count',
        
        # Meteor altitude bins (many fields!)
        'alt_70_80km': '70-80 km',
        'alt_75_100km': '75-100 km',
        'alt_lt_90km': '< 90 km',
        'alt_80_90km': '80-90 km',
        'alt_90_100km': '90-100 km',
        'alt_100_110km': '100-110 km',
        'alt_110_120km': '110-120 km',
        'alt_120_130km': '120-130 km',
        'alt_130_140km': '130-140 km',
        'alt_140_150km': '140-150 km',
        'alt_150_160km': '150-160 km',
        'alt_160_170km': '160-170 km',
        'alt_170_180km': '170-180 km',
        'alt_180_190km': '180-190 km',
        'alt_190_200km': '190-200 km',
        'alt_200_210km': '200-210 km',
        'alt_210_220km': '210-220 km',
        'alt_201_225km': '201-225 km',
        'alt_220_230km': '220-230 km',
        'alt_230_240km': '230-240 km',
        'alt_226_250km': '226-250 km',
        'alt_240_250km': '240-250 km',
        'alt_250_260km': '250-260 km',
        'alt_260_270km': '260-270 km',
        'alt_270_280km': '270-280 km',
        'alt_280_290km': '280-290 km',
        'alt_290_300km': '290-300 km',
        'alt_gt_250km': '> 250 km',
        'alt_300_310km': '300-310 km',
        'alt_310_320km': '310-320 km',
        'alt_320_330km': '320-330 km',
        'alt_330_340km': '330-340 km',
        'alt_340_350km': '340-350 km',
        'alt_noname': 'Altitude (unspecified)',
        
        # Radio science
        'scaling_factor': 'Scaling Factor',
        'offset_val': 'Offset Value',
        'cent_freq': 'Center Frequency (MHz)',
        'bandwidth': 'Bandwidth (MHz)',
        'beamsize': 'Beam Size (arcmin)',
        'beam_elong': 'Beam Elongation',
        'beam_rotation': 'Beam Rotation (deg)',
        'derived_max': 'Derived Maximum',
        'derived_min': 'Derived Minimum',
        'spectrum_rows': 'Spectrum Rows',
        'spectrum_cols': 'Spectrum Columns',
        'velo_min': 'Velocity Min (km/s)',
        'velo_interval': 'Velocity Interval (km/s)',
        'freq_min': 'Frequency Min (MHz)',
        'freq_interval': 'Frequency Interval (MHz)',
        
        # RHC/LHC (Right/Left Hand Circular polarization)
        'rhc_rows': 'RHC Spectrum Rows',
        'rhc_scaling_factor': 'RHC Scaling Factor',
        'rhc_offset': 'RHC Offset',
        'rhc_freq_min': 'RHC Frequency Min (MHz)',
        'rhc_freq_interval': 'RHC Frequency Interval (MHz)',
        'rhc_derived_max': 'RHC Maximum',
        'rhc_derived_min': 'RHC Minimum',
        'lhc_rows': 'LHC Spectrum Rows',
        'lhc_scaling_factor': 'LHC Scaling Factor',
        'lhc_offset': 'LHC Offset',
        'lhc_freq_min': 'LHC Frequency Min (MHz)',
        'lhc_freq_interval': 'LHC Frequency Interval (MHz)',
        'lhc_derived_max': 'LHC Maximum',
        'lhc_derived_min': 'LHC Minimum',
        
        # Amateur network
        'guiding': 'Guiding',
        'dev_tech': 'Development Technique',
        'power_1': 'Magnification (primary)',
        'power_2': 'Magnification (secondary)',
        'power_3': 'Magnification (tertiary)',
        
        # Infrared
        'lambda_eff': 'Effective Wavelength (μm)',
        'irphot_type': 'IR Photometry Type',
        
        # Miscellaneous
        'syscode': 'System Code',
    }



def categorize_metadata_fields(metadata_obj):
    """
    Categorize metadata fields into logical groups for organized display.
    
    Args:
        metadata_obj: Discipline-specific metadata model instance
        
    Returns:
        OrderedDict of {category_name: [(field_name, field_label, field_value), ...]}
    """
    from collections import OrderedDict
    
    if not metadata_obj:
        return OrderedDict()
    
    # Skip these system/FK fields
    skip_fields = {'id', 'meta_common', 'meta_common_id'}
    
    # Get comprehensive field labels
    field_labels = get_comprehensive_field_labels()
    
    # Define field categories
    categories = OrderedDict([
        ('Instrument & Telescope', [
            'instrument', 'instrume', 'config', 'aperture', 'fratio', 'foc_len',
            'telefl', 'detector', 'cameraid', 'chip_id'
        ]),
        ('Observation Parameters', [
            'exposure', 'duration', 'integration_time', 'airmass', 'airm_mid',
            'elevation', 'apsize', 'observing_aperture', 'telescope_aperture',
            'aperture_diam', 'observer', 'obs_code', 'obs_num', 'observer_id'
        ]),
        ('Filter & Wavelength', [
            'filter', 'filter_name', 'filterid', 'emulsion', 'iso', 'iso_din',
            'hypsen', 'hypersense', 'center_wavelength', 'wavelength', 'bandpass',
            'bandwidth', 'lambda_eff'
        ]),
        ('Field of View', [
            'fov_x', 'fov_y', 'fov1', 'fov2'
        ]),
        ('Image Metadata', [
            'naxis', 'naxis1', 'naxis2', 'bitpix', 'bscale', 'bzero', 'blank', 'bunit',
            'image_lines', 'image_samples', 'size', 'maxcol', 'maxrow', 'orgcol',
            'orgrow', 'pixel_scale', 'pltscale', 'pltsze1', 'pltsze2', 'pltype'
        ]),
        ('WCS Coordinates', [
            'cdelt1', 'cdelt2', 'crval1', 'crval2', 'crpix1', 'crpix2',
            'crota1', 'crota2', 'ctype1', 'ctype2', 'equinox'
        ]),
        ('Coordinates & Position', [
            'ra', 'decl', 'dec', 'ra_reported', 'dec_reported', 'ra_head', 'dec_head',
            'ra_cpme', 'dec_cpme', 'ra_rms', 'dec_rms', 'jd', 'utc_corr',
            'elev_obs', 'lat_calc_flag'
        ]),
        ('Offset from Nucleus', [
            'offset_rho', 'offset_theta', 'rho', 'theta', 'separ_nucl', 'dxy', 'dz'
        ]),
        ('Photometry & Magnitude', [
            'magnitude', 'mag_total', 'mag_nucleus', 'mag_error', 'mag_lt',
            'lim_mag', 'lim_magn', 'mag_limit', 'log_flux', 'flux_error',
            'limit_flag', 'flux_unit'
        ]),
        ('Polarimetry & Stokes', [
            'polarization', 'polariz_error', 'polariz_angle', 'polariz_angle_err',
            'polariz_type', 'q_over_i', 'q_over_i_err', 'u_over_i', 'u_over_i_err',
            'v_over_i', 'v_over_i_err'
        ]),
        ('Spectroscopy', [
            'ssn_num', 'resolution', 'resolut', 'res_unit', 'res_code', 'range_lo',
            'range_hi', 'spectral_range_lo', 'spectral_range_hi', 'slit_size',
            'slit_pa', 'slit_width', 'slit_height', 'dis_code', 'axes', 'axis_1',
            'axis_2', 'spectrum_notes'
        ]),
        ('Astrometry', [
            'filenum', 'nref', 'npos', 'ref_cat', 'method', 'rmsa', 'rmsd',
            'uncertainty_a', 'uncertainty_b', 'position_angle'
        ]),
        ('Scan Parameters', [
            'scnstpx', 'scnstpy', 'scnstep', 'scnstp', 'scnapr'
        ]),
        ('Calibration', [
            'calibration', 'calibration_flag', 'ncalspot', 'ncalwdge', 'cometmax',
            'skyden', 'skymin', 'skyunf', 'sense'
        ]),
        ('Quality & Flags', [
            'data_quality', 'image_qual', 'quality', 'acceptance_flag',
            'image_quality', 'note_flag', 'note_code', 'spec_evt'
        ]),
        ('Data Format', [
            'dat_form', 'dat_type'
        ]),
        ('Processing Dates', [
            'date_pds', 'date_prc', 'date_rec', 'date_rel', 'date_wrt'
        ]),
        ('Comments', [
            'cmts_anl', 'cmts_log', 'cmts_obs', 'cmts_prc', 'cmts_log_alt',
            'log_cmts', 'obs_cmts'
        ]),
        ('Origin & Submitter', [
            'origin', 'orging', 'submittr', 'file_num', 'obslog', 'obs_site_id',
            'observatory_id', 'lon_obs', 'lat_obs', 'long_obs', 'ppn_num', 'idno', 'syscode'
        ]),
        ('Meteor Shower Data', [
            'shower', 'system', 'limit_sensitiv', 'direction', 'total_count',
            'rads_count', 'total_meteor_count', 'count_shower', 'count_noshower',
            'cloud_cover', 'site_num', 'site_name', 'source_fileid', 'source_filepathid'
        ]),
        ('Meteor Duration Bins', [
            'dur_lt_h', 'dur_gt_h', 'dur_ge_1', 'dur_gt_1', 'dur_ge_8', 'dur_gt_8',
            'net_time_count'
        ]),
        ('Meteor Altitude Distribution', [
            'alt_70_80km', 'alt_75_100km', 'alt_lt_90km', 'alt_80_90km', 'alt_90_100km',
            'alt_100_110km', 'alt_110_120km', 'alt_120_130km', 'alt_130_140km',
            'alt_140_150km', 'alt_150_160km', 'alt_160_170km', 'alt_170_180km',
            'alt_180_190km', 'alt_190_200km', 'alt_200_210km', 'alt_210_220km',
            'alt_201_225km', 'alt_220_230km', 'alt_230_240km', 'alt_226_250km',
            'alt_240_250km', 'alt_250_260km', 'alt_260_270km', 'alt_270_280km',
            'alt_280_290km', 'alt_290_300km', 'alt_gt_250km', 'alt_300_310km',
            'alt_310_320km', 'alt_320_330km', 'alt_330_340km', 'alt_340_350km',
            'alt_noname'
        ]),
        ('Radio Science', [
            'scaling_factor', 'offset_val', 'cent_freq', 'bandwidth', 'beamsize',
            'beam_elong', 'beam_rotation', 'derived_max', 'derived_min',
            'spectrum_rows', 'spectrum_cols', 'velo_min', 'velo_interval',
            'freq_min', 'freq_interval'
        ]),
        ('Radio - RHC Polarization', [
            'rhc_rows', 'rhc_scaling_factor', 'rhc_offset', 'rhc_freq_min',
            'rhc_freq_interval', 'rhc_derived_max', 'rhc_derived_min'
        ]),
        ('Radio - LHC Polarization', [
            'lhc_rows', 'lhc_scaling_factor', 'lhc_offset', 'lhc_freq_min',
            'lhc_freq_interval', 'lhc_derived_max', 'lhc_derived_min'
        ]),
        ('Amateur Network', [
            'guiding', 'dev_tech', 'power_1', 'power_2', 'power_3'
        ]),
        ('Infrared', [
            'irphot_type'
        ]),
    ])
    
    # Collect all fields with values
    field_data = {}
    for field in metadata_obj._meta.get_fields():
        if field.name in skip_fields:
            continue
        value = getattr(metadata_obj, field.name, None)
        if value is not None and value != '':
            field_data[field.name] = value
    
    # Organize fields into categories
    result = OrderedDict()
    categorized_fields = set()
    
    for category_name, field_names in categories.items():
        category_fields = []
        for field_name in field_names:
            if field_name in field_data:
                label = field_labels.get(field_name, field_name.replace('_', ' ').title())
                category_fields.append((field_name, label, field_data[field_name]))
                categorized_fields.add(field_name)
        
        if category_fields:
            result[category_name] = category_fields
    
    # Add any uncategorized fields to "Other"
    uncategorized = []
    for field_name, value in field_data.items():
        if field_name not in categorized_fields:
            label = field_labels.get(field_name, field_name.replace('_', ' ').title())
            uncategorized.append((field_name, label, value))
    
    if uncategorized:
        result['Other'] = uncategorized
    
    return result


def format_metadata_value(field_name, value, metadata_obj):
    """
    Format metadata field value for display, potentially resolving foreign keys.
    
    Args:
        field_name: Name of the field
        value: Raw field value
        metadata_obj: Metadata model instance
        
    Returns:
        Formatted string value
    """
    # Handle foreign keys by looking up related objects
    if field_name == 'observatory_id' and value:
        try:
            obs = ApxIhwObscodes.objects.get(id=value)
            if obs.location:
                return f"{obs.observatory} ({obs.location})"
            return obs.observatory
        except ApxIhwObscodes.DoesNotExist:
            return f"Observatory #{value}"
    
    if field_name == 'observer_id' and value:
        return f"Observer #{value}"
    
    # Format boolean fields
    if isinstance(value, bool):
        return 'Yes' if value else 'No'
    
    # Format single-character flags
    if field_name in ['calibration_flag', 'hypsen', 'hypersense', 'guiding', 'dark_adapt']:
        if value == 'Y' or value == 'y':
            return 'Yes'
        elif value == 'N' or value == 'n':
            return 'No'
        elif value == 'U':
            return 'Unknown'
        return str(value)
    
    # Format numeric values with appropriate precision
    if isinstance(value, float):
        # Coordinates and angles - 4 decimal places
        if any(s in field_name for s in ['ra', 'dec', 'lat', 'lon', 'crval', 'cdelt']):
            return f"{value:.4f}"
        # Wavelengths, flux - 3 decimal places
        elif any(s in field_name for s in ['wavelength', 'flux', 'mag']):
            return f"{value:.3f}"
        # Other floats - 2 decimal places
        else:
            return f"{value:.2f}"
    
    # Return string representation for everything else
    return str(value)
