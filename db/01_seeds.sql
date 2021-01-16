insert into market_types(name)
values
('Emerging'),
('Developed ex US'),
('US');

insert into investments(market_type_id, ticker_symbol)
select mt.id, x.ticker_symbol
from market_types mt
join (
  values
  ('ADRE'),
  ('AVEM'),
  ('BKEM'),
  ('CEY'),
  ('CEZ'),
  ('DBEM'),
  ('DEM'),
  ('DFAE'),
  ('DGRE'),
  ('DGS'),
  ('DVYE'),
  ('ECON'),
  ('ECOW'),
  ('EDIV'),
  ('EDOG'),
  ('EELV'),
  ('EEM'),
  ('EEMD'),
  ('EEMO'),
  ('EEMS'),
  ('EEMV'),
  ('EEMX'),
  ('EMDV'),
  ('EMFM'),
  ('EMGF'),
  ('EMMF'),
  ('EMSG'),
  ('EMXC'),
  ('EMXF'),
  ('ESGE'),
  ('EWX'),
  ('EYLD'),
  ('FDEM'),
  ('FEM'),
  ('FEMS'),
  ('FLQE'),
  ('FNDE'),
  ('FRDM'),
  ('GEM'),
  ('GSEE'),
  ('GVAL'),
  ('HEEM'),
  ('IEMG'),
  ('ISEM'),
  ('JHEM'),
  ('JPEM'),
  ('KEMX'),
  ('LDEM'),
  ('MFEM'),
  ('NUEM'),
  ('OBOR'),
  ('PBEE'),
  ('PIE'),
  ('PXH'),
  ('QEMM'),
  ('QLVE'),
  ('RESE'),
  ('RFEM'),
  ('RNEM'),
  ('ROAM'),
  ('SCHE'),
  ('SDEM'),
  ('SPEM'),
  ('TLEH'),
  ('TLTE'),
  ('UEVM'),
  ('VWO'),
  ('XCEM'),
  ('XSOE')
) as x(ticker_symbol) on true
where mt.name = 'Emerging';


insert into investments(market_type_id, ticker_symbol)
select mt.id, x.ticker_symbol
from market_types mt
join (
  values
  ('ACSG'), -- contains China and Taiwan
  ('ACWX'), -- contains China
  ('AVDE'),
  ('AVDV'),
  ('BBEU'), -- limited to Europe
  ('BBIN'),
  ('BKIE'),
  ('CEFA'),
  ('CID'),
  ('CIL'),
  ('CIZ'),
  ('CWI'),  -- contains China
  ('DBAW'), -- contains China
  ('DBEF'),
  ('DBEU'), -- limited to Europe
  ('DBEZ'),
  ('DDLS'),
  ('DDWM'),
  ('DEEF'),
  ('DEFA'),
  ('DFAI'),
  ('DFE'),  -- limited to Europe
  ('DIM'),
  ('DLS'),
  ('DMDV'),
  ('DMXF'),
  ('DNL'),
  ('DOL'),
  ('DOO'),
  ('DTH'),
  ('DWM'),
  ('DWMF'),
  ('DWX'),
  ('EASG'),
  ('EFA'),
  ('EFAD'),
  ('EFAS'),
  ('EFAV'),
  ('EFAX'),
  ('EFG'),
  ('EFV'),
  ('ERSX'), -- contains China
  ('ESGD'),
  ('ESGN'),
  ('EUDG'), -- limited to Europe
  ('EZU'),  -- limited to Europe
  ('FDD'),  -- limited to Europe
  ('FDEV'),
  ('FDT'),
  ('FDTS'),
  ('FEP'),  -- limited to Europe
  ('FEUZ'), -- limited to Europe
  ('FFSG'),
  ('FFTG'),
  ('FGD'),
  ('FICS'),
  ('FID'), -- contains South Korea
  ('FIDI'),
  ('FIVA'),
  ('FLEE'), -- limited to Europe
  ('FLEH'), -- limited to Europe
  ('FLQH'),
  ('FNDC'), -- contains South Korea
  ('FNDF'), -- contains South Korea
  ('FYLD'),
  ('GSEU'), -- limited to Europe
  ('GSID'),
  ('GSIE'),
  ('GWX'),  -- contains South Korea
  ('GXF'),  -- limited to Denmark, Sweden, Finland, Norway
  ('HAWX'), -- contains China
  ('HDAW'), -- contains China
  ('HDEF'),
  ('HDMV'),
  ('HEFA'),
  ('HEZU'), -- limited to Europe
  ('HFXI'), -- contains South Korea
  ('HSCZ'),
  ('ICOW'), -- contains South Korea
  ('IDEV'),
  ('IDHD'),
  ('IDHQ'),
  ('IDLB'), -- contains South Korea
  ('IDLV'),
  ('IDMO'),
  ('IDOG'),
  ('IDV'),
  ('IEFA'),
  ('IEUR'), -- limited to Europe
  ('IEUS'), -- limited to Europe
  ('IEV'),  -- limited to Europe
  ('IGRO'), -- contains China
  ('IHDG'),
  ('IJAN'),
  ('IJUL'),
  ('IMOM'),
  ('IMTM'),
  ('INTF'),
  ('IPKW'), -- contains India
  ('IQDE'), -- contains China, Taiwan
  ('IQDF'), -- contains China, Taiwan
  ('IQDG'),
  ('IQDY'), -- contains China
  ('IQIN'),
  ('IQLT'),
  ('IQSI'),
  ('ISCF'),
  ('ISDX'), -- contains South Korea
  ('ISZE'),
  ('IVAL'),
  ('IVLU'),
  ('IXUS'), -- contains China
  ('JHMD'),
  ('JIG'),  -- contains China
  ('JPIN'),
  ('LVHI'),
  ('MFDX'),
  ('MOTI'), -- contains China
  ('NUDM'),
  ('OVF'),  -- contains China
  ('PBDM'), -- contains South Korea
  ('PDEV'),
  ('PDN'),
  ('PIZ'),
  ('PQIN'),
  ('PTIN'),
  ('PXF'), -- contains South Korea
  ('QEFA'),
  ('QINT'),
  ('QLVD'),
  ('RBIN'),
  ('RESD'),
  ('RFDI'),
  ('RFEU'), -- limited to Europe
  ('RNDM'),
  ('RODM'),
  ('SCHC'), -- contains South Korea
  ('SCHF'),
  ('SCZ'),
  ('SPDW'),
  ('SPEU'), -- limited to Europe
  ('TLDH'),
  ('TLTD'),
  ('TPIF'),
  ('TTAI'),
  ('UIVM'),
  ('VEA'),
  ('VEU'),
  ('VGK'),  -- limited to Europe
  ('VIGI'), -- contains China
  ('VSGX'), -- contains China
  ('VSS'),  -- contains Taiwan, China, South Korea
  ('VT'),   -- contains China
  ('VWID'),
  ('VXUS'), -- contains China
  ('VYMI'), -- contains China, Taiwan
  ('WWJD'), -- contains Brazil, India
  ('YDEC')
) as x(ticker_symbol) on true
where mt.name = 'Developed ex US';
