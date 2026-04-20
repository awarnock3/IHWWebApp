/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.11.14-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: ihwdb2
-- ------------------------------------------------------
-- Server version	10.11.14-MariaDB-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `apx_am_obs_site`
--

DROP TABLE IF EXISTS `apx_am_obs_site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `apx_am_obs_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `observer` varchar(24) NOT NULL,
  `site` int(11) NOT NULL,
  `longitude` decimal(9,6) DEFAULT NULL,
  `latitude` decimal(9,6) DEFAULT NULL,
  `altitude` int(11) DEFAULT NULL,
  `resolve` varchar(12) DEFAULT NULL,
  `country` int(11) DEFAULT NULL,
  `note` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `country` (`country`),
  CONSTRAINT `apx_am_obs_site_ibfk_1` FOREIGN KEY (`country`) REFERENCES `apx_ihw_country` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=3483 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Observatory site appendix for Amateur Observations Network';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `apx_ihw_country`
--

DROP TABLE IF EXISTS `apx_ihw_country`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `apx_ihw_country` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` int(11) NOT NULL,
  `country` varchar(40) NOT NULL,
  `template` varchar(8) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_apx_ccode` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=181 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='IHW Country Code Appendix';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `apx_ihw_obscodes`
--

DROP TABLE IF EXISTS `apx_ihw_obscodes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `apx_ihw_obscodes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `system` varchar(10) NOT NULL,
  `observatory` varchar(40) NOT NULL,
  `location` varchar(40) DEFAULT NULL,
  `instrument` varchar(60) DEFAULT NULL,
  `lon` float DEFAULT NULL,
  `lat` float DEFAULT NULL,
  `subdiscipline` int(11) DEFAULT NULL,
  `telescope` varchar(40) DEFAULT NULL,
  `aperture` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_system` (`system`),
  KEY `subdiscipline` (`subdiscipline`),
  CONSTRAINT `apx_ihw_obscodes_ibfk_1` FOREIGN KEY (`subdiscipline`) REFERENCES `ihw_subnet` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1198 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='IHW observatory site data appendix';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `apx_msn_counts`
--

DROP TABLE IF EXISTS `apx_msn_counts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `apx_msn_counts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `object` varchar(20) NOT NULL,
  `year` int(11) NOT NULL,
  `source` varchar(40) DEFAULT NULL,
  `num_hours` int(11) NOT NULL,
  `subnet` varchar(16) NOT NULL,
  `notes` varchar(40) DEFAULT NULL,
  `msn_num` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `subnet` (`subnet`),
  CONSTRAINT `apx_msn_counts_ibfk_1` FOREIGN KEY (`subnet`) REFERENCES `ihw_subnet` (`subnet`)
) ENGINE=InnoDB AUTO_INCREMENT=119 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='IHW Meteor Studies counts appendix';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `apx_msn_obscodes`
--

DROP TABLE IF EXISTS `apx_msn_obscodes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `apx_msn_obscodes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `system` varchar(16) NOT NULL,
  `station` varchar(40) NOT NULL,
  `subnet` varchar(8) NOT NULL,
  `lon` float DEFAULT NULL,
  `lat` float DEFAULT NULL,
  `elevation` int(11) DEFAULT NULL,
  `freq` float DEFAULT NULL,
  `peak_power` float DEFAULT NULL,
  `pulse_repet` float DEFAULT NULL,
  `pulse_dur` float DEFAULT NULL,
  `min_line_dens` varchar(12) DEFAULT NULL,
  `antenna` text DEFAULT NULL,
  `notes` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `subnet` (`subnet`),
  CONSTRAINT `apx_msn_obscodes_ibfk_1` FOREIGN KEY (`subnet`) REFERENCES `ihw_subnet` (`subnet`)
) ENGINE=InnoDB AUTO_INCREMENT=327 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='IHW Meteor Studies Network observatory codes appendix';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `apx_msnvis_observers`
--

DROP TABLE IF EXISTS `apx_msnvis_observers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `apx_msnvis_observers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `observer` varchar(24) NOT NULL,
  `number` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_number` (`number`)
) ENGINE=InnoDB AUTO_INCREMENT=523 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='IHW Meteor Studies observer appendix';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `apx_msnvis_sites`
--

DROP TABLE IF EXISTS `apx_msnvis_sites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `apx_msnvis_sites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `site` varchar(32) NOT NULL,
  `number` int(11) DEFAULT NULL,
  `longitude` decimal(9,6) DEFAULT NULL,
  `latitude` decimal(9,6) DEFAULT NULL,
  `elevation` int(11) DEFAULT NULL,
  `note` text DEFAULT NULL,
  `subdiscipline` varchar(16) NOT NULL DEFAULT 'MSNVIS',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_number` (`number`),
  KEY `subdiscipline` (`subdiscipline`),
  CONSTRAINT `apx_msnvis_sites_ibfk_1` FOREIGN KEY (`subdiscipline`) REFERENCES `ihw_subnet` (`subnet`)
) ENGINE=InnoDB AUTO_INCREMENT=315 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='IHW Meteor Studies visual sites appendix';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `apx_pflx_notes`
--

DROP TABLE IF EXISTS `apx_pflx_notes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `apx_pflx_notes` (
  `note_code` tinyint(4) NOT NULL,
  `note_text` text NOT NULL,
  PRIMARY KEY (`note_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Explanatory notes for PFLX flux reprocessing, referenced by idx_meta_pflx.note_code';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_amdr`
--

DROP TABLE IF EXISTS `idx_meta_amdr`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_amdr` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `meta_common_id` int(11) NOT NULL,
  `scale` decimal(7,4) DEFAULT NULL COMMENT 'arcmin/mm',
  `aperture` decimal(7,4) DEFAULT NULL COMMENT 'meters',
  `instrument` varchar(4) DEFAULT NULL COMMENT 'instrument type code',
  `fratio` decimal(5,1) DEFAULT NULL,
  `power_1` smallint(6) DEFAULT NULL,
  `power_2` smallint(6) DEFAULT NULL,
  `power_3` smallint(6) DEFAULT NULL,
  `duration` smallint(6) DEFAULT NULL COMMENT 'minutes',
  `lim_magn` decimal(4,1) DEFAULT NULL COMMENT 'limiting magnitude',
  `obs_site_id` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_amdr_meta` (`meta_common_id`),
  CONSTRAINT `fk_amdr_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2589 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='IHW Amateur Studies Drawings subnet metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_ampg`
--

DROP TABLE IF EXISTS `idx_meta_ampg`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_ampg` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `meta_common_id` int(11) NOT NULL,
  `foc_len` decimal(7,4) DEFAULT NULL COMMENT 'focal length, meters',
  `fratio` decimal(5,1) DEFAULT NULL,
  `aperture` decimal(7,4) DEFAULT NULL COMMENT 'meters',
  `fov1` decimal(6,2) DEFAULT NULL COMMENT 'degrees',
  `fov2` decimal(6,2) DEFAULT NULL COMMENT 'degrees',
  `duration` decimal(8,2) DEFAULT NULL,
  `emulsion` varchar(14) DEFAULT NULL,
  `iso_din` varchar(8) DEFAULT NULL,
  `hypersense` char(1) DEFAULT NULL COMMENT 'Y=yes C=color N=no',
  `guiding` char(1) DEFAULT NULL,
  `idno` varchar(8) DEFAULT NULL,
  `obs_site_id` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_ampg_meta` (`meta_common_id`),
  CONSTRAINT `fk_ampg_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4341 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='IHW Amateur Studies Photographic subnet metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_amsp`
--

DROP TABLE IF EXISTS `idx_meta_amsp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_amsp` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `meta_common_id` int(11) NOT NULL,
  `config` varchar(8) DEFAULT NULL COMMENT 'spectrograph configuration',
  `instrument` varchar(4) DEFAULT NULL,
  `foc_len` decimal(7,4) DEFAULT NULL COMMENT 'meters',
  `fratio` decimal(5,1) DEFAULT NULL,
  `aperture` decimal(7,4) DEFAULT NULL COMMENT 'meters',
  `duration` decimal(7,2) DEFAULT NULL,
  `emulsion` varchar(14) DEFAULT NULL,
  `iso` varchar(8) DEFAULT NULL,
  `hypsen` char(1) DEFAULT NULL,
  `guiding` char(1) DEFAULT NULL,
  `idno` varchar(8) DEFAULT NULL,
  `obs_site_id` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_amsp_meta` (`meta_common_id`),
  CONSTRAINT `fk_amsp_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=91 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='IHW Amateur Studies Spectral subnet metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_amvis`
--

DROP TABLE IF EXISTS `idx_meta_amvis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_amvis` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `meta_common_id` int(11) NOT NULL,
  `mag_gt` char(1) DEFAULT NULL COMMENT 'greater-than flag',
  `magnitude` decimal(5,1) DEFAULT NULL,
  `mag_comment` char(1) DEFAULT NULL,
  `mag_est_method` char(1) DEFAULT NULL,
  `chart` varchar(8) DEFAULT NULL,
  `coma_maj` decimal(6,1) DEFAULT NULL COMMENT 'arcmin',
  `coma_min` decimal(6,1) DEFAULT NULL COMMENT 'arcmin',
  `degree_cond` tinyint(4) DEFAULT NULL COMMENT '0-9 scale',
  `tail_len` decimal(6,2) DEFAULT NULL COMMENT 'degrees',
  `tail_pos_ang` smallint(6) DEFAULT NULL COMMENT 'degrees',
  `aperture` decimal(7,4) DEFAULT NULL COMMENT 'meters',
  `instrument` varchar(4) DEFAULT NULL,
  `fratio` decimal(5,1) DEFAULT NULL,
  `power` smallint(6) DEFAULT NULL,
  `lim_mag` decimal(5,1) DEFAULT NULL,
  `lim_mag_comment` varchar(5) DEFAULT NULL,
  `dark_adapt` char(1) DEFAULT NULL COMMENT 'Y/N',
  `obs_site_id` smallint(6) DEFAULT NULL,
  `elevation` smallint(6) DEFAULT NULL COMMENT 'meters',
  `special_event_flag` char(1) DEFAULT NULL,
  `instrument_full` varchar(14) DEFAULT NULL,
  `tail_len_2` decimal(6,2) DEFAULT NULL COMMENT 'degrees',
  `tail_pos_ang_2` smallint(6) DEFAULT NULL COMMENT 'degrees',
  `tail_len_3` decimal(6,2) DEFAULT NULL COMMENT 'degrees',
  `tail_pos_ang_3` smallint(6) DEFAULT NULL COMMENT 'degrees',
  PRIMARY KEY (`id`),
  KEY `fk_amvis_meta` (`meta_common_id`),
  CONSTRAINT `fk_amvis_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=46565 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='IHW Amateur Studies Visual subnet metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_astrom`
--

DROP TABLE IF EXISTS `idx_meta_astrom`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_astrom` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `jd` double NOT NULL COMMENT 'Julian Date of observation',
  `ra_reported` float NOT NULL COMMENT 'RA as reported, decimal degrees',
  `dec_reported` float NOT NULL COMMENT 'Dec as reported, decimal degrees',
  `ra` float NOT NULL COMMENT 'RA corrected, decimal degrees',
  `decl` float NOT NULL COMMENT 'Dec corrected, decimal degrees',
  `acceptance_flag` varchar(1) DEFAULT NULL COMMENT 'A=accepted, D=rejected',
  `image_quality` varchar(1) DEFAULT NULL,
  `ra_rms` float NOT NULL COMMENT 'RA RMS error (arcsec)',
  `dec_rms` float NOT NULL COMMENT 'Dec RMS error (arcsec)',
  `utc_corr` float DEFAULT NULL COMMENT 'ET-UTC correction (sec)',
  `lon_obs` float NOT NULL COMMENT 'Observatory longitude, decimal degrees',
  `lat_obs` float NOT NULL COMMENT 'Observatory latitude, decimal degrees',
  `lat_calc_flag` varchar(1) DEFAULT NULL COMMENT '+/- N/S calculated - not used',
  `dxy` smallint(6) DEFAULT NULL COMMENT 'Topocentric parallax DXY (m)',
  `dz` smallint(6) DEFAULT NULL COMMENT 'Topocentric parallax DZ (m)',
  `mag_total` float DEFAULT NULL COMMENT 'Total magnitude (NULL if unknown)',
  `mag_nucleus` float DEFAULT NULL COMMENT 'Nuclear magnitude (NULL if unknown)',
  `filenum` int(11) DEFAULT NULL COMMENT 'IHW file number (1986 data only)',
  `obs_code` varchar(3) NOT NULL COMMENT 'Observatory code',
  `observer` varchar(24) NOT NULL,
  `observatory_id` int(11) DEFAULT NULL,
  `meta_common_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_astrom_ra` (`ra`),
  KEY `idx_astrom_decl` (`decl`),
  KEY `idx_astrom_jd` (`jd`),
  KEY `fk_astr_meta` (`meta_common_id`),
  KEY `fk_astr_observatory` (`observatory_id`),
  CONSTRAINT `fk_astr_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`),
  CONSTRAINT `fk_astr_observatory` FOREIGN KEY (`observatory_id`) REFERENCES `apx_ihw_obscodes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24988 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Astrometry network observation metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_common`
--

DROP TABLE IF EXISTS `idx_meta_common`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_common` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `discipline` varchar(8) NOT NULL COMMENT 'Discipline/subnet code (e.g. ASTR, IRIM)',
  `date_obs` datetime NOT NULL COMMENT 'UTC observation datetime',
  `net_num` int(11) NOT NULL COMMENT 'Discipline-specific observation identifier',
  `syscode` varchar(8) NOT NULL COMMENT 'IHW system code from FITS SYSTEM',
  `observer` varchar(64) NOT NULL DEFAULT 'unknown',
  `note_flag` tinyint(1) NOT NULL DEFAULT 0 COMMENT '1 if notes are present',
  `filename` varchar(32) NOT NULL COMMENT 'Source data file root name (no extension)',
  `note` text DEFAULT NULL,
  `object` varchar(24) NOT NULL DEFAULT '1P/Halley',
  `idxfileid` int(11) DEFAULT NULL COMMENT 'FK to ihw_files.fileid (NULL if no data file)',
  `linenum` int(11) NOT NULL COMMENT 'Line number within source file',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_common_obs` (`discipline`,`idxfileid`,`linenum`),
  KEY `idx_common_date` (`date_obs`),
  KEY `idx_common_discipline` (`discipline`),
  KEY `idx_common_net_num` (`net_num`),
  KEY `idx_common_observer` (`observer`(16)),
  KEY `fk_common_fileid` (`idxfileid`),
  CONSTRAINT `fk_common_fileid` FOREIGN KEY (`idxfileid`) REFERENCES `ihw_files` (`fileid`)
) ENGINE=InnoDB AUTO_INCREMENT=332406 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Cross-discipline common metadata for all IHW networks';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_irim`
--

DROP TABLE IF EXISTS `idx_meta_irim`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_irim` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `filter` varchar(10) NOT NULL COMMENT 'Filter name (e.g. K, H, N)',
  `image_lines` smallint(6) DEFAULT NULL,
  `image_samples` smallint(6) DEFAULT NULL,
  `pixel_scale` float DEFAULT NULL COMMENT 'Arcsec per pixel',
  `flux_unit` varchar(20) DEFAULT NULL COMMENT 'Flux unit (e.g. MJY/PIX)',
  `syscode` varchar(12) NOT NULL,
  `observatory_id` int(11) DEFAULT NULL,
  `meta_common_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_irim_meta` (`meta_common_id`),
  KEY `fk_IRIM_observatory` (`observatory_id`),
  CONSTRAINT `fk_IRIM_observatory` FOREIGN KEY (`observatory_id`) REFERENCES `apx_ihw_obscodes` (`id`),
  CONSTRAINT `fk_irim_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=520 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='IR Imaging Network label metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_irph`
--

DROP TABLE IF EXISTS `idx_meta_irph`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_irph` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `irphot_type` varchar(12) NOT NULL COMMENT 'magnitude, flux, or addenda',
  `syscode` varchar(12) NOT NULL,
  `observatory_id` int(11) DEFAULT NULL,
  `meta_common_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_irph_meta` (`meta_common_id`),
  KEY `fk_IRPH_observatory` (`observatory_id`),
  CONSTRAINT `fk_IRPH_observatory` FOREIGN KEY (`observatory_id`) REFERENCES `apx_ihw_obscodes` (`id`),
  CONSTRAINT `fk_irph_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=961 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='IR Photometry Network label metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_irpol`
--

DROP TABLE IF EXISTS `idx_meta_irpol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_irpol` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `syscode` varchar(12) NOT NULL,
  `observatory_id` int(11) DEFAULT NULL,
  `meta_common_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_irpol_meta` (`meta_common_id`),
  KEY `fk_IRPOL_observatory` (`observatory_id`),
  CONSTRAINT `fk_IRPOL_observatory` FOREIGN KEY (`observatory_id`) REFERENCES `apx_ihw_obscodes` (`id`),
  CONSTRAINT `fk_irpol_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='IR Polarimetry Network label metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_irsp`
--

DROP TABLE IF EXISTS `idx_meta_irsp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_irsp` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `spectral_range_lo` float DEFAULT NULL COMMENT 'Low end of spectral range (microns)',
  `spectral_range_hi` float DEFAULT NULL COMMENT 'High end of spectral range (microns)',
  `resolution` float DEFAULT NULL COMMENT 'Spectral resolution (microns)',
  `aperture` float DEFAULT NULL COMMENT 'Aperture size (arcseconds)',
  `syscode` varchar(12) NOT NULL,
  `observatory_id` int(11) DEFAULT NULL,
  `meta_common_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_irsp_meta` (`meta_common_id`),
  KEY `fk_IRSP_observatory` (`observatory_id`),
  CONSTRAINT `fk_IRSP_observatory` FOREIGN KEY (`observatory_id`) REFERENCES `apx_ihw_obscodes` (`id`),
  CONSTRAINT `fk_irsp_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=337 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='IR Spectroscopy Network label metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_lspn`
--

DROP TABLE IF EXISTS `idx_meta_lspn`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_lspn` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `observer` varchar(64) DEFAULT NULL COMMENT 'FITS OBSERVER keyword',
  `emulsion` varchar(25) DEFAULT NULL COMMENT 'Photographic emulsion type',
  `filter_name` varchar(25) DEFAULT NULL,
  `exposure` float DEFAULT NULL COMMENT 'Exposure duration (seconds)',
  `fov_x` float DEFAULT NULL COMMENT 'Field of view X (degrees)',
  `fov_y` float DEFAULT NULL COMMENT 'Field of view Y (degrees)',
  `calibration_flag` char(1) DEFAULT NULL COMMENT 'T=calibration available',
  `data_quality` varchar(20) DEFAULT NULL COMMENT 'FITS QUALITY value',
  `observatory_id` int(11) DEFAULT NULL COMMENT 'FK to apx_ihw_obscodes.id for LSPN SYSTEM',
  `airm_mid` float DEFAULT NULL,
  `aperture` float DEFAULT NULL,
  `apsize` float DEFAULT NULL,
  `bitpix` smallint(6) DEFAULT NULL,
  `blank` float DEFAULT NULL,
  `bscale` double DEFAULT NULL,
  `bunit` varchar(32) DEFAULT NULL,
  `bzero` double DEFAULT NULL,
  `cameraid` varchar(16) DEFAULT NULL,
  `cdelt1` double DEFAULT NULL,
  `cdelt2` double DEFAULT NULL,
  `chip_id` varchar(32) DEFAULT NULL,
  `cmts_anl` varchar(80) DEFAULT NULL,
  `cmts_log` varchar(80) DEFAULT NULL,
  `cmts_obs` varchar(80) DEFAULT NULL,
  `cmts_prc` varchar(80) DEFAULT NULL,
  `cmts_log_alt` varchar(80) DEFAULT NULL COMMENT 'Value from FITS CMTS_LOG keyword',
  `cometmax` float DEFAULT NULL,
  `crota1` double DEFAULT NULL,
  `crota2` double DEFAULT NULL,
  `crpix1` double DEFAULT NULL,
  `crpix2` double DEFAULT NULL,
  `crval1` double DEFAULT NULL,
  `crval2` double DEFAULT NULL,
  `ctype1` varchar(16) DEFAULT NULL,
  `ctype2` varchar(16) DEFAULT NULL,
  `dat_form` varchar(16) DEFAULT NULL,
  `dat_type` varchar(16) DEFAULT NULL,
  `date_pds` varchar(8) DEFAULT NULL,
  `date_prc` varchar(8) DEFAULT NULL,
  `date_rec` varchar(8) DEFAULT NULL,
  `date_rel` varchar(8) DEFAULT NULL,
  `date_wrt` varchar(8) DEFAULT NULL,
  `dec_cpme` double DEFAULT NULL,
  `dec_head` double DEFAULT NULL,
  `detector` varchar(32) DEFAULT NULL,
  `elev_obs` smallint(6) DEFAULT NULL,
  `equinox` float DEFAULT NULL,
  `file_num` int(11) DEFAULT NULL,
  `filterid` varchar(8) DEFAULT NULL,
  `fratio` float DEFAULT NULL,
  `hypsen` char(1) DEFAULT NULL,
  `instrume` varchar(16) DEFAULT NULL,
  `lat_obs` varchar(16) DEFAULT NULL,
  `log_cmts` varchar(80) DEFAULT NULL,
  `long_obs` varchar(16) DEFAULT NULL,
  `maxcol` smallint(6) DEFAULT NULL,
  `maxrow` smallint(6) DEFAULT NULL,
  `naxis` tinyint(4) DEFAULT NULL,
  `naxis1` int(11) DEFAULT NULL,
  `naxis2` int(11) DEFAULT NULL,
  `ncalspot` smallint(6) DEFAULT NULL,
  `ncalwdge` smallint(6) DEFAULT NULL,
  `obs_cmts` varchar(80) DEFAULT NULL,
  `obslog` varchar(20) DEFAULT NULL,
  `orgcol` smallint(6) DEFAULT NULL,
  `orging` varchar(32) DEFAULT NULL,
  `orgrow` smallint(6) DEFAULT NULL,
  `origin` varchar(32) DEFAULT NULL,
  `pltscale` float DEFAULT NULL,
  `pltsze1` float DEFAULT NULL,
  `pltsze2` float DEFAULT NULL,
  `pltype` char(1) DEFAULT NULL,
  `ra_cpme` double DEFAULT NULL,
  `ra_head` double DEFAULT NULL,
  `scnapr` smallint(6) DEFAULT NULL,
  `scnstep` smallint(6) DEFAULT NULL,
  `scnstp` smallint(6) DEFAULT NULL,
  `scnstpx` smallint(6) DEFAULT NULL,
  `scnstpy` smallint(6) DEFAULT NULL,
  `sense` char(1) DEFAULT NULL,
  `size` varchar(16) DEFAULT NULL,
  `skyden` smallint(6) DEFAULT NULL,
  `skymin` float DEFAULT NULL,
  `skyunf` varchar(8) DEFAULT NULL,
  `spec_evt` char(1) DEFAULT NULL,
  `submittr` varchar(16) DEFAULT NULL,
  `meta_common_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_lspn_observatory` (`observatory_id`),
  KEY `fk_lspn_meta` (`meta_common_id`),
  CONSTRAINT `fk_lspn_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`),
  CONSTRAINT `fk_lspn_observatory` FOREIGN KEY (`observatory_id`) REFERENCES `apx_ihw_obscodes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11160 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Large-Scale Phenomena Network FITS header metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_msnrdr`
--

DROP TABLE IF EXISTS `idx_meta_msnrdr`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_msnrdr` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `meta_common_id` int(11) NOT NULL,
  `shower` varchar(20) DEFAULT NULL COMMENT 'Meteor shower name (e.g., ETA AQUARID, ORIONID)',
  `system` varchar(8) DEFAULT NULL COMMENT 'IHW system code (FK to apx_msn_obscodes.system)',
  `limit_sensitiv` varchar(22) DEFAULT NULL COMMENT 'Radar limiting sensitivity',
  `direction` char(1) DEFAULT NULL COMMENT 'Antenna direction indicator',
  `total_count` smallint(6) DEFAULT NULL COMMENT 'Total meteor echo count',
  `rads_count` smallint(6) DEFAULT NULL COMMENT 'Radiant-related echo count',
  `dur_lt_h` smallint(6) DEFAULT NULL COMMENT 'Echo duration < 0.5 sec count',
  `dur_gt_h` smallint(6) DEFAULT NULL COMMENT 'Echo duration > 0.5 sec count',
  `dur_ge_1` smallint(6) DEFAULT NULL COMMENT 'Echo duration >= 1 sec count',
  `dur_gt_1` float DEFAULT NULL COMMENT 'Echo duration > 1 sec (rate)',
  `dur_ge_8` smallint(6) DEFAULT NULL COMMENT 'Echo duration >= 8 sec count',
  `dur_gt_8` float DEFAULT NULL COMMENT 'Echo duration > 8 sec (rate)',
  `net_time_count` float DEFAULT NULL COMMENT 'Net observation time count',
  `alt_70_80km` smallint(6) DEFAULT NULL COMMENT 'Echo count 70-80 km altitude',
  `alt_75_100km` smallint(6) DEFAULT NULL COMMENT 'Echo count 75-100 km altitude',
  `alt_lt_90km` smallint(6) DEFAULT NULL COMMENT 'Echo count < 90 km altitude',
  `alt_80_90km` smallint(6) DEFAULT NULL COMMENT 'Echo count 80-90 km altitude',
  `alt_90_100km` smallint(6) DEFAULT NULL COMMENT 'Echo count 90-100 km altitude',
  `alt_100_110km` smallint(6) DEFAULT NULL COMMENT 'Echo count 100-110 km altitude',
  `alt_110_120km` smallint(6) DEFAULT NULL COMMENT 'Echo count 110-120 km altitude',
  `alt_120_130km` smallint(6) DEFAULT NULL COMMENT 'Echo count 120-130 km altitude',
  `alt_130_140km` smallint(6) DEFAULT NULL COMMENT 'Echo count 130-140 km altitude',
  `alt_140_150km` smallint(6) DEFAULT NULL COMMENT 'Echo count 140-150 km altitude',
  `alt_150_160km` smallint(6) DEFAULT NULL COMMENT 'Echo count 150-160 km altitude',
  `alt_160_170km` smallint(6) DEFAULT NULL COMMENT 'Echo count 160-170 km altitude',
  `alt_170_180km` smallint(6) DEFAULT NULL COMMENT 'Echo count 170-180 km altitude',
  `alt_180_190km` smallint(6) DEFAULT NULL COMMENT 'Echo count 180-190 km altitude',
  `alt_190_200km` smallint(6) DEFAULT NULL COMMENT 'Echo count 190-200 km altitude',
  `alt_200_210km` smallint(6) DEFAULT NULL COMMENT 'Echo count 200-210 km altitude',
  `alt_210_220km` smallint(6) DEFAULT NULL COMMENT 'Echo count 210-220 km altitude',
  `alt_201_225km` smallint(6) DEFAULT NULL COMMENT 'Echo count 201-225 km altitude',
  `alt_220_230km` smallint(6) DEFAULT NULL COMMENT 'Echo count 220-230 km altitude',
  `alt_230_240km` smallint(6) DEFAULT NULL COMMENT 'Echo count 230-240 km altitude',
  `alt_226_250km` smallint(6) DEFAULT NULL COMMENT 'Echo count 226-250 km altitude',
  `alt_240_250km` smallint(6) DEFAULT NULL COMMENT 'Echo count 240-250 km altitude',
  `alt_250_260km` smallint(6) DEFAULT NULL COMMENT 'Echo count 250-260 km altitude',
  `alt_260_270km` smallint(6) DEFAULT NULL COMMENT 'Echo count 260-270 km altitude',
  `alt_270_280km` smallint(6) DEFAULT NULL COMMENT 'Echo count 270-280 km altitude',
  `alt_280_290km` smallint(6) DEFAULT NULL COMMENT 'Echo count 280-290 km altitude',
  `alt_290_300km` smallint(6) DEFAULT NULL COMMENT 'Echo count 290-300 km altitude',
  `alt_noname` smallint(6) DEFAULT NULL COMMENT 'Echo count unclassified altitude',
  `alt_gt_250km` smallint(6) DEFAULT NULL COMMENT 'Echo count > 250 km altitude',
  `alt_300_310km` smallint(6) DEFAULT NULL COMMENT 'Echo count 300-310 km altitude',
  `alt_310_320km` smallint(6) DEFAULT NULL COMMENT 'Echo count 310-320 km altitude',
  `alt_320_330km` smallint(6) DEFAULT NULL COMMENT 'Echo count 320-330 km altitude',
  `alt_330_340km` smallint(6) DEFAULT NULL COMMENT 'Echo count 330-340 km altitude',
  `alt_340_350km` smallint(6) DEFAULT NULL COMMENT 'Echo count 340-350 km altitude',
  PRIMARY KEY (`id`),
  KEY `fk_msnrdr_meta` (`meta_common_id`),
  CONSTRAINT `fk_msnrdr_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20887 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='IHW Meteor Studies Radar Network (MSNRDR) per-observation metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_msnvis`
--

DROP TABLE IF EXISTS `idx_meta_msnvis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_msnvis` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `meta_common_id` int(11) NOT NULL,
  `shower` varchar(20) DEFAULT NULL COMMENT 'Meteor shower name (e.g., ORIONID, ETA AQUARID)',
  `site_num` smallint(6) DEFAULT NULL COMMENT 'FK to apx_msnvis_sites.number',
  `site_name` varchar(20) DEFAULT NULL COMMENT 'Observation site name',
  `obs_num` smallint(6) DEFAULT NULL COMMENT 'FK to apx_msnvis_observers.number',
  `observer_id` int(11) DEFAULT NULL COMMENT 'FK to apx_msnvis_observers.id',
  `total_meteor_count` smallint(6) DEFAULT NULL COMMENT 'Total meteor count or observation duration (archive label: TOTAL_METEOR_COUNT)',
  `count_shower` smallint(6) DEFAULT NULL COMMENT 'Number of shower meteors observed',
  `count_noshower` smallint(6) DEFAULT NULL COMMENT 'Number of non-shower meteors observed',
  `mag_limit` float DEFAULT NULL COMMENT 'Limiting magnitude',
  `cloud_cover` tinyint(4) DEFAULT NULL COMMENT 'Cloud cover percentage (0-100)',
  `source_fileid` int(11) DEFAULT NULL COMMENT 'FK component to ihw_file_filepath.fileid for source label file',
  `source_filepathid` int(11) DEFAULT NULL COMMENT 'FK component to ihw_file_filepath.filepathid for source label file',
  PRIMARY KEY (`id`),
  KEY `fk_msnvis_source_file` (`source_fileid`,`source_filepathid`),
  KEY `fk_msnvis_observer` (`observer_id`),
  KEY `fk_msnvis_meta` (`meta_common_id`),
  CONSTRAINT `fk_msnvis_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`),
  CONSTRAINT `fk_msnvis_observer` FOREIGN KEY (`observer_id`) REFERENCES `apx_msnvis_observers` (`id`),
  CONSTRAINT `fk_msnvis_source_file` FOREIGN KEY (`source_fileid`, `source_filepathid`) REFERENCES `ihw_file_filepath` (`fileid`, `filepathid`)
) ENGINE=InnoDB AUTO_INCREMENT=3249 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='IHW Meteor Studies Visual Network (MSNVIS) per-observation metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_nnsn`
--

DROP TABLE IF EXISTS `idx_meta_nnsn`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_nnsn` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `filter_name` varchar(25) DEFAULT NULL,
  `exposure` float DEFAULT NULL COMMENT 'Exposure duration (seconds)',
  `airmass` float DEFAULT NULL,
  `data_quality` varchar(10) DEFAULT NULL,
  `image_lines` smallint(6) DEFAULT NULL,
  `image_samples` smallint(6) DEFAULT NULL,
  `pixel_scale` float DEFAULT NULL COMMENT 'Arcsec per pixel',
  `flux_unit` varchar(20) DEFAULT NULL,
  `observatory_id` int(11) DEFAULT NULL COMMENT 'FK to apx_ihw_obscodes.id for NNSN SYSTEM',
  `airm_mid` float DEFAULT NULL,
  `aperture` float DEFAULT NULL,
  `apsize` float DEFAULT NULL,
  `bitpix` smallint(6) DEFAULT NULL,
  `bunit` varchar(64) DEFAULT NULL,
  `cometmax` int(11) DEFAULT NULL,
  `crota1` varchar(16) DEFAULT NULL,
  `dat_form` varchar(16) DEFAULT NULL,
  `date_rel` varchar(8) DEFAULT NULL,
  `date_wrt` varchar(8) DEFAULT NULL,
  `elev_obs` smallint(6) DEFAULT NULL,
  `naxis` tinyint(4) DEFAULT NULL,
  `origin` varchar(32) DEFAULT NULL,
  `sense` varchar(3) DEFAULT NULL,
  `skymin` int(11) DEFAULT NULL,
  `spec_evt` char(1) DEFAULT NULL,
  `submittr` varchar(24) DEFAULT NULL,
  `telefl` float DEFAULT NULL,
  `meta_common_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_nnsn_observatory` (`observatory_id`),
  KEY `fk_nnsn_meta` (`meta_common_id`),
  CONSTRAINT `fk_nnsn_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`),
  CONSTRAINT `fk_nnsn_observatory` FOREIGN KEY (`observatory_id`) REFERENCES `apx_ihw_obscodes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10570 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Near-Nucleus Studies Network image metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_pflx`
--

DROP TABLE IF EXISTS `idx_meta_pflx`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_pflx` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `filter_name` varchar(10) DEFAULT NULL,
  `center_wavelength` int(11) DEFAULT NULL COMMENT 'Filter center wavelength (Angstrom)',
  `bandpass` int(11) DEFAULT NULL COMMENT 'Filter FWHM (Angstrom)',
  `limit_flag` char(1) DEFAULT NULL COMMENT '< = upper limit; NULL = detected',
  `log_flux` float DEFAULT NULL COMMENT 'Log10 observed flux (erg/s/cm2/Angstrom)',
  `flux_error` float DEFAULT NULL COMMENT 'Error in log10 flux; NULL = not reported',
  `observing_aperture` float DEFAULT NULL COMMENT 'Aperture diameter (arcsec); NULL = not reported',
  `rho` int(11) DEFAULT NULL COMMENT 'Radial offset from peak brightness (arcsec)',
  `theta` int(11) DEFAULT NULL COMMENT 'Position angle of aperture offset (degrees E of N)',
  `integration_time` int(11) DEFAULT NULL COMMENT 'Integration time (seconds); NULL = not reported',
  `airmass` float DEFAULT NULL,
  `observatory_id` int(11) DEFAULT NULL COMMENT 'FK to apx_ihw_obscodes.id for PFLX SYSTEM',
  `telescope_aperture` float DEFAULT NULL COMMENT 'Telescope aperture (meters); NULL = not reported',
  `note_code` tinyint(4) DEFAULT NULL COMMENT 'Note reference code (1-40); NULL = no note',
  `meta_common_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_pflx_meta` (`meta_common_id`),
  KEY `fk_pflx_note` (`note_code`),
  KEY `fk_pflx_observatory` (`observatory_id`),
  CONSTRAINT `fk_pflx_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`),
  CONSTRAINT `fk_pflx_note` FOREIGN KEY (`note_code`) REFERENCES `apx_pflx_notes` (`note_code`),
  CONSTRAINT `fk_pflx_observatory` FOREIGN KEY (`observatory_id`) REFERENCES `apx_ihw_obscodes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=74189 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Photometric Flux Network narrowband measurement metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_pmag`
--

DROP TABLE IF EXISTS `idx_meta_pmag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_pmag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `meta_common_id` int(11) NOT NULL,
  `ppn_num` int(11) DEFAULT NULL COMMENT 'PPN observer/instrument program number',
  `filter_name` varchar(4) DEFAULT NULL COMMENT 'Filter name (V, B, R, GT, RT, etc.)',
  `wavelength` smallint(6) DEFAULT NULL COMMENT 'Filter central wavelength (Angstroms)',
  `bandpass` smallint(6) DEFAULT NULL COMMENT 'Filter bandpass (Angstroms)',
  `aperture_diam` float DEFAULT NULL COMMENT 'Aperture diameter (arcsec)',
  `duration` smallint(6) DEFAULT NULL COMMENT 'Integration time (seconds)',
  `mag_lt` char(1) DEFAULT NULL COMMENT 'Limit flag: > = upper limit',
  `magnitude` float DEFAULT NULL COMMENT 'Observed magnitude',
  `mag_error` float DEFAULT NULL COMMENT 'Magnitude uncertainty (mag)',
  `offset_rho` smallint(6) DEFAULT NULL COMMENT 'Offset from nucleus (arcsec)',
  `offset_theta` smallint(6) DEFAULT NULL COMMENT 'Offset position angle (degrees)',
  `airmass` float DEFAULT NULL COMMENT 'Airmass at time of observation',
  `note_flag` char(1) DEFAULT NULL COMMENT 'T if notes exist for this observation',
  PRIMARY KEY (`id`),
  KEY `fk_pmag_meta` (`meta_common_id`),
  CONSTRAINT `fk_pmag_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11671 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='IHW Photometry broadband magnitude (PMAG) subnet metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_ppol`
--

DROP TABLE IF EXISTS `idx_meta_ppol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_ppol` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `meta_common_id` int(11) NOT NULL,
  `ppn_num` int(11) DEFAULT NULL COMMENT 'PPN observer/instrument program number',
  `filter_name` varchar(4) DEFAULT NULL COMMENT 'Filter name',
  `wavelength` smallint(6) DEFAULT NULL COMMENT 'Filter central wavelength (Angstroms)',
  `bandpass` smallint(6) DEFAULT NULL COMMENT 'Filter bandpass (Angstroms)',
  `aperture_diam` float DEFAULT NULL COMMENT 'Aperture diameter (arcsec)',
  `duration` smallint(6) DEFAULT NULL COMMENT 'Integration time (seconds)',
  `polariz_type` varchar(2) DEFAULT NULL COMMENT 'Polarization type (LN=linear, CC=circular)',
  `polarization` float DEFAULT NULL COMMENT 'Polarization degree (percent)',
  `polariz_error` float DEFAULT NULL COMMENT 'Polarization uncertainty (percent)',
  `polariz_angle` float DEFAULT NULL COMMENT 'Polarization position angle (degrees)',
  `polariz_angle_err` float DEFAULT NULL COMMENT 'Position angle uncertainty (degrees)',
  `offset_rho` smallint(6) DEFAULT NULL COMMENT 'Offset from nucleus (arcsec)',
  `offset_theta` smallint(6) DEFAULT NULL COMMENT 'Offset position angle (degrees)',
  `airmass` float DEFAULT NULL COMMENT 'Airmass at time of observation',
  `note_flag` char(1) DEFAULT NULL COMMENT 'T if notes exist for this observation',
  PRIMARY KEY (`id`),
  KEY `fk_ppol_meta` (`meta_common_id`),
  CONSTRAINT `fk_ppol_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2404 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='IHW Photometry polarization (PPOL) subnet metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_psto`
--

DROP TABLE IF EXISTS `idx_meta_psto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_psto` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `meta_common_id` int(11) NOT NULL,
  `ppn_num` int(11) DEFAULT NULL COMMENT 'PPN observer/instrument program number',
  `filter_name` varchar(4) DEFAULT NULL COMMENT 'Filter name',
  `wavelength` smallint(6) DEFAULT NULL COMMENT 'Filter central wavelength (Angstroms)',
  `bandpass` smallint(6) DEFAULT NULL COMMENT 'Filter bandpass (Angstroms)',
  `aperture_diam` float DEFAULT NULL COMMENT 'Aperture diameter (arcsec)',
  `duration` smallint(6) DEFAULT NULL COMMENT 'Integration time (seconds)',
  `q_over_i` float DEFAULT NULL COMMENT 'Stokes Q/I parameter',
  `q_over_i_err` float DEFAULT NULL COMMENT 'Stokes Q/I uncertainty',
  `u_over_i` float DEFAULT NULL COMMENT 'Stokes U/I parameter',
  `u_over_i_err` float DEFAULT NULL COMMENT 'Stokes U/I uncertainty',
  `v_over_i` float DEFAULT NULL COMMENT 'Stokes V/I parameter',
  `v_over_i_err` float DEFAULT NULL COMMENT 'Stokes V/I uncertainty',
  `offset_rho` smallint(6) DEFAULT NULL COMMENT 'Offset from nucleus (arcsec)',
  `offset_theta` smallint(6) DEFAULT NULL COMMENT 'Offset position angle (degrees)',
  `airmass` float DEFAULT NULL COMMENT 'Airmass at time of observation',
  `note_flag` char(1) DEFAULT NULL COMMENT 'T if notes exist for this observation',
  PRIMARY KEY (`id`),
  KEY `fk_psto_meta` (`meta_common_id`),
  CONSTRAINT `fk_psto_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=397 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='IHW Photometry Stokes parameters (PSTO) subnet metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_rscn`
--

DROP TABLE IF EXISTS `idx_meta_rscn`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_rscn` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `image_lines` int(11) DEFAULT NULL COMMENT 'Image rows (LINES)',
  `image_samples` int(11) DEFAULT NULL COMMENT 'Image columns (LINE_SAMPLES)',
  `scaling_factor` float DEFAULT NULL COMMENT 'Physical = raw * scaling_factor + offset',
  `offset_val` float DEFAULT NULL,
  `cent_freq` float DEFAULT NULL COMMENT 'Center frequency (MHz)',
  `bandwidth` float DEFAULT NULL COMMENT 'Bandwidth (MHz)',
  `beamsize` float DEFAULT NULL COMMENT 'Beam size (arcsec)',
  `beam_elong` float DEFAULT NULL COMMENT 'Beam elongation',
  `beam_rotation` float DEFAULT NULL COMMENT 'Beam rotation (degrees)',
  `dat_type` varchar(10) DEFAULT NULL COMMENT '6-char IHW data type code',
  `meta_common_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_rscn_meta` (`meta_common_id`),
  CONSTRAINT `fk_rscn_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Radio Studies Continuum Network (RSCN) observation metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_rsoc`
--

DROP TABLE IF EXISTS `idx_meta_rsoc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_rsoc` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `image_lines` int(11) DEFAULT NULL COMMENT 'Image rows (LINES)',
  `image_samples` int(11) DEFAULT NULL COMMENT 'Image columns (LINE_SAMPLES)',
  `scaling_factor` float DEFAULT NULL,
  `offset_val` float DEFAULT NULL,
  `derived_max` float DEFAULT NULL COMMENT 'Derived maximum flux density (Jy)',
  `derived_min` float DEFAULT NULL COMMENT 'Derived minimum flux density (Jy)',
  `cent_freq` float DEFAULT NULL COMMENT 'Center frequency (MHz)',
  `bandwidth` float DEFAULT NULL COMMENT 'Bandwidth (MHz)',
  `beamsize` float DEFAULT NULL,
  `beam_elong` float DEFAULT NULL,
  `beam_rotation` float DEFAULT NULL,
  `dat_type` varchar(10) DEFAULT NULL,
  `meta_common_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_rsoc_meta` (`meta_common_id`),
  CONSTRAINT `fk_rsoc_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Radio Studies Occultation Continuum (RSOC) observation metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_rsoh`
--

DROP TABLE IF EXISTS `idx_meta_rsoh`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_rsoh` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `spectrum_rows` int(11) DEFAULT NULL COMMENT 'Number of spectral channels',
  `scaling_factor` float DEFAULT NULL,
  `offset_val` float DEFAULT NULL,
  `derived_max` float DEFAULT NULL COMMENT 'Max flux density (Jy)',
  `derived_min` float DEFAULT NULL COMMENT 'Min flux density (Jy)',
  `velo_min` float DEFAULT NULL COMMENT 'Minimum velocity (m/s, VELO-COM frame)',
  `velo_interval` float DEFAULT NULL COMMENT 'Velocity channel spacing (m/s)',
  `cent_freq` float DEFAULT NULL COMMENT 'Center frequency (MHz)',
  `bandwidth` float DEFAULT NULL COMMENT 'Bandwidth (MHz)',
  `beamsize` float DEFAULT NULL,
  `beam_elong` float DEFAULT NULL,
  `beam_rotation` float DEFAULT NULL,
  `dat_type` varchar(10) DEFAULT NULL,
  `meta_common_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_rsoh_meta` (`meta_common_id`),
  CONSTRAINT `fk_rsoh_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20302 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Radio Studies OH spectral line (RSOH) velocity spectrum metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_rsrdr`
--

DROP TABLE IF EXISTS `idx_meta_rsrdr`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_rsrdr` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `rhc_rows` int(11) DEFAULT NULL COMMENT 'RHC spectrum rows',
  `rhc_scaling_factor` float DEFAULT NULL,
  `rhc_offset` float DEFAULT NULL,
  `rhc_freq_min` float DEFAULT NULL COMMENT 'RHC minimum frequency offset (Hz)',
  `rhc_freq_interval` float DEFAULT NULL COMMENT 'RHC frequency channel interval (Hz)',
  `rhc_derived_max` float DEFAULT NULL,
  `rhc_derived_min` float DEFAULT NULL,
  `lhc_rows` int(11) DEFAULT NULL COMMENT 'LHC spectrum rows',
  `lhc_scaling_factor` float DEFAULT NULL,
  `lhc_offset` float DEFAULT NULL,
  `lhc_freq_min` float DEFAULT NULL COMMENT 'LHC minimum frequency offset (Hz)',
  `lhc_freq_interval` float DEFAULT NULL COMMENT 'LHC frequency channel interval (Hz)',
  `lhc_derived_max` float DEFAULT NULL,
  `lhc_derived_min` float DEFAULT NULL,
  `cent_freq` float DEFAULT NULL COMMENT 'Center frequency (MHz)',
  `bandwidth` float DEFAULT NULL COMMENT 'Bandwidth (MHz)',
  `dat_type` varchar(10) DEFAULT NULL,
  `meta_common_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_rsrdr_meta` (`meta_common_id`),
  CONSTRAINT `fk_rsrdr_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Radio Studies Radar (RSRDR) RHC+LHC polarization spectrum metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_rssl`
--

DROP TABLE IF EXISTS `idx_meta_rssl`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_rssl` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `spectrum_rows` int(11) DEFAULT NULL COMMENT 'Number of spectral channels',
  `scaling_factor` float DEFAULT NULL,
  `offset_val` float DEFAULT NULL,
  `derived_max` float DEFAULT NULL COMMENT 'Max flux density (Jy)',
  `derived_min` float DEFAULT NULL COMMENT 'Min flux density (Jy)',
  `velo_min` float DEFAULT NULL COMMENT 'Minimum velocity (m/s, VELO-COM frame)',
  `velo_interval` float DEFAULT NULL COMMENT 'Velocity channel spacing (m/s)',
  `cent_freq` float DEFAULT NULL COMMENT 'Center frequency (MHz)',
  `bandwidth` float DEFAULT NULL COMMENT 'Bandwidth (MHz)',
  `beamsize` float DEFAULT NULL,
  `beam_elong` float DEFAULT NULL,
  `beam_rotation` float DEFAULT NULL,
  `dat_type` varchar(10) DEFAULT NULL,
  `meta_common_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_rssl_meta` (`meta_common_id`),
  CONSTRAINT `fk_rssl_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=842 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Radio Studies Spectral Line (RSSL) velocity spectrum metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_rsuv`
--

DROP TABLE IF EXISTS `idx_meta_rsuv`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_rsuv` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `spectrum_rows` int(11) DEFAULT NULL COMMENT 'Number of visibility records (ROWS)',
  `spectrum_cols` int(11) DEFAULT NULL COMMENT 'Number of columns per record (COLUMNS=16)',
  `freq_min` float DEFAULT NULL COMMENT 'Minimum frequency (Hz)',
  `freq_interval` float DEFAULT NULL COMMENT 'Frequency channel spacing (Hz)',
  `scaling_factor` float DEFAULT NULL COMMENT 'Visibility scaling factor',
  `cent_freq` float DEFAULT NULL COMMENT 'Center frequency (MHz)',
  `bandwidth` float DEFAULT NULL COMMENT 'Bandwidth (MHz)',
  `dat_type` varchar(10) DEFAULT NULL,
  `meta_common_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_rsuv_meta` (`meta_common_id`),
  CONSTRAINT `fk_rsuv_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=251 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Radio Studies UV Interferometry (RSUV) visibility metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `idx_meta_spectra`
--

DROP TABLE IF EXISTS `idx_meta_spectra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `idx_meta_spectra` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `meta_common_id` int(11) NOT NULL,
  `ssn_num` int(11) DEFAULT NULL COMMENT 'SSN observation number (SSN_NUM / FILENUM)',
  `dat_form` varchar(10) DEFAULT NULL COMMENT 'Data format (e.g. STANDARD)',
  `dat_type` varchar(20) DEFAULT NULL COMMENT 'Data type (e.g. RAW DIGITAL)',
  `dis_code` varchar(12) DEFAULT NULL COMMENT 'IHW discipline/observer code',
  `calibration` char(1) DEFAULT NULL COMMENT 'Calibration flag (T/F)',
  `resolution` decimal(10,3) DEFAULT NULL COMMENT 'Spectral resolution from netspect (text form)',
  `range_lo` int(11) DEFAULT NULL COMMENT 'Wavelength range low end (Angstroms)',
  `range_hi` int(11) DEFAULT NULL COMMENT 'Wavelength range high end (Angstroms)',
  `exposure` decimal(10,2) DEFAULT NULL COMMENT 'Exposure time (seconds)',
  `aperture` varchar(80) DEFAULT NULL COMMENT 'Aperture description',
  `slit_size` varchar(10) DEFAULT NULL COMMENT 'Slit dimensions',
  `slit_pa` decimal(6,1) DEFAULT NULL COMMENT 'Slit position angle (degrees)',
  `airmass` decimal(6,3) DEFAULT NULL COMMENT 'Airmass at mid-observation',
  `axes` tinyint(4) DEFAULT NULL COMMENT 'Number of data axes',
  `axis_1` smallint(6) DEFAULT NULL COMMENT 'Size of axis 1',
  `axis_2` smallint(6) DEFAULT NULL COMMENT 'Size of axis 2',
  `separ_nucl` decimal(8,1) DEFAULT NULL COMMENT 'Separation from nucleus (arcsec)',
  `offset_rho` decimal(8,1) DEFAULT NULL COMMENT 'Offset rho from nucleus (arcsec)',
  `offset_theta` smallint(6) DEFAULT NULL COMMENT 'Offset position angle (degrees)',
  `elevation` decimal(7,1) DEFAULT NULL COMMENT 'Observatory elevation (metres)',
  `quality` varchar(10) DEFAULT NULL COMMENT 'Data quality flag',
  PRIMARY KEY (`id`),
  KEY `fk_spectra_meta` (`meta_common_id`),
  CONSTRAINT `fk_spectra_meta` FOREIGN KEY (`meta_common_id`) REFERENCES `idx_meta_common` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37001 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Spectroscopy Studies Network (SSN) per-observation metadata';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ihw_ephemeris`
--

DROP TABLE IF EXISTS `ihw_ephemeris`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ihw_ephemeris` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comet` enum('Halley','Crommelin','GZ') NOT NULL DEFAULT 'Halley',
  `fileid` int(11) NOT NULL,
  `date` date NOT NULL,
  `year` smallint(6) DEFAULT NULL,
  `month` tinyint(4) DEFAULT NULL,
  `day` tinyint(4) DEFAULT NULL,
  `hour` float DEFAULT NULL COMMENT 'Decimal hours (UT)',
  `jday` double DEFAULT NULL COMMENT 'Julian Date',
  `ra` float DEFAULT NULL COMMENT 'RA decimal degrees (J2000)',
  `decl` float DEFAULT NULL COMMENT 'Dec decimal degrees (J2000)',
  `delta` float DEFAULT NULL COMMENT 'Geocentric distance (AU)',
  `deldot` float DEFAULT NULL COMMENT 'Geocentric radial velocity (km/s)',
  `r` float DEFAULT NULL COMMENT 'Heliocentric distance (AU)',
  `rdot` float DEFAULT NULL COMMENT 'Heliocentric radial velocity (km/s)',
  `theta` float DEFAULT NULL COMMENT 'Solar elongation (deg)',
  `beta` float DEFAULT NULL COMMENT 'Solar latitude (deg)',
  `moon` float DEFAULT NULL COMMENT 'Lunar distance (deg)',
  `psang` float DEFAULT NULL COMMENT 'Position angle sun-comet (deg)',
  `psamv` float DEFAULT NULL COMMENT 'Position angle comet velocity (deg)',
  PRIMARY KEY (`id`),
  KEY `idx_jd` (`jday`),
  KEY `idx_date` (`date`),
  KEY `idx_position` (`ra`,`decl`),
  KEY `fk_ephem_fileid` (`fileid`),
  CONSTRAINT `fk_ephem_fileid` FOREIGN KEY (`fileid`) REFERENCES `ihw_files` (`fileid`)
) ENGINE=InnoDB AUTO_INCREMENT=5535 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='IHW comet ephemeris data';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ihw_file_filepath`
--

DROP TABLE IF EXISTS `ihw_file_filepath`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ihw_file_filepath` (
  `fileid` int(11) NOT NULL,
  `filepathid` int(11) NOT NULL,
  UNIQUE KEY `uniq_fileid_filepathid` (`fileid`,`filepathid`),
  KEY `fk_filepath_id` (`filepathid`),
  CONSTRAINT `fk_file_fileid` FOREIGN KEY (`fileid`) REFERENCES `ihw_files` (`fileid`),
  CONSTRAINT `fk_filepath_id` FOREIGN KEY (`filepathid`) REFERENCES `ihw_filepath` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Utility link table between files and file paths';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ihw_filepath`
--

DROP TABLE IF EXISTS `ihw_filepath`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ihw_filepath` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dirpath` varchar(512) NOT NULL COMMENT 'Directory path relative to archive root, no leading or trailing slash',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_dirpath` (`dirpath`)
) ENGINE=InnoDB AUTO_INCREMENT=4131 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Directory paths for archive files (relative to configured root)';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ihw_files`
--

DROP TABLE IF EXISTS `ihw_files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ihw_files` (
  `fileid` int(11) NOT NULL AUTO_INCREMENT,
  `filename` varchar(64) NOT NULL,
  `network_id` int(11) NOT NULL,
  `network` varchar(8) NOT NULL,
  `subnet` varchar(16) NOT NULL,
  `subnet_id` int(11) NOT NULL,
  `type` varchar(16) NOT NULL,
  `arch_ver` varchar(8) NOT NULL,
  `digest` varchar(32) NOT NULL,
  `filesize` bigint(20) NOT NULL COMMENT 'File size in bytes',
  PRIMARY KEY (`fileid`),
  UNIQUE KEY `uniq_digest` (`digest`),
  KEY `idx_filename` (`filename`),
  KEY `idx_digest` (`digest`),
  KEY `fk_files_network_id` (`network_id`),
  KEY `fk_files_subnet_id` (`subnet_id`),
  CONSTRAINT `fk_files_network` FOREIGN KEY (`network_id`) REFERENCES `ihw_network` (`id`),
  CONSTRAINT `fk_files_subnet` FOREIGN KEY (`subnet_id`) REFERENCES `ihw_subnet` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=136329 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Master list of unique archive files, identified by MD5 digest';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ihw_network`
--

DROP TABLE IF EXISTS `ihw_network`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ihw_network` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `netnum` int(11) NOT NULL,
  `discipline` varchar(8) NOT NULL,
  `name` varchar(32) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Master list of IHW Network disciplines';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ihw_subnet`
--

DROP TABLE IF EXISTS `ihw_subnet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ihw_subnet` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subnet` varchar(16) NOT NULL,
  `subnet_name` varchar(32) DEFAULT NULL,
  `discipline` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_subnet` (`subnet`),
  KEY `discipline` (`discipline`),
  CONSTRAINT `ihw_subnet_ibfk_1` FOREIGN KEY (`discipline`) REFERENCES `ihw_network` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Master list of IHW discipline subnets';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-19 15:23:42
