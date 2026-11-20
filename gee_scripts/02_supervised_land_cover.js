var SITE_GEOMETRIES = {"aws_pdx": [[[-119.64171195208215, 45.81800973804475], [-119.63429296194695, 45.8180321700963], [-119.63383778657992, 45.81812409215994], [-119.62763950444914, 45.81813904683127], [-119.62761412100413, 45.81829961862225], [-119.62517331080058, 45.81832578921197], [-119.6251947684727, 45.82055398288432], [-119.62525404980258, 45.820627992663724], [-119.62750174095706, 45.82087099464729], [-119.62901450684146, 45.82087473313103], [-119.63007129719333, 45.82077753247144], [-119.63051117947177, 45.820598084653994], [-119.63057555248812, 45.82051583754439], [-119.63146068146304, 45.820508360528414], [-119.63154114773349, 45.82058686914621], [-119.63215805580691, 45.820762578508734], [-119.63524796059207, 45.82083360979578], [-119.64057482769564, 45.82081491736061], [-119.64174963524417, 45.82077005549056], [-119.64171195208215, 45.81800973804475]]], "h5_quincy2": [[[-119.82651628939323, 47.24827861001804], [-119.82653774706534, 47.246902109174705], [-119.82416667429618, 47.24692395867382], [-119.82416667429618, 47.24835143975411], [-119.82651628939323, 47.24827861001804]]]};
// Supervised land-cover workflow: one site's FULL 2.5 km AOI per run.
// Geometry configuration is copied from dip_pipeline/config.py.
// Run twice (aws_pdx / h5_quincy2). Python also supports pooled training.
// Reference labels must come from dated imagery/field interpretation.
// Do NOT label from NDVI/NDBI rules or assume every built-up pixel is a DC.
var SITE_ID = 'h5_quincy2';
var YEAR = 2025;
var INCLUDE_THERMAL = false; // true exports LST/EMIS too, requiring valid thermal pixels.
var LABEL_ASSET = ''; // Optional: projects/YOUR_PROJECT/assets/reference_polygons
// Alternative: draw/import a FeatureCollection named reference_polygons.
// Each feature needs land_cover_class (1..4), reference_id, reference_date
// (YYYY-MM-DD, matching YEAR), and reference_source (citation/image ID).
// Use unique reference_id values for distinct homogeneous reference areas.
// Draw reference polygons in multiple separated parts of the FULL AOI.

var campus = ee.Geometry.Polygon(SITE_GEOMETRIES[SITE_ID]);
var aoi = campus.buffer(2500, 1);
Map.setOptions('SATELLITE');
Map.centerObject(campus, 13);
Map.addLayer(ee.FeatureCollection([ee.Feature(aoi)]).style({
  color: 'yellow', fillColor: '00000000'}), {}, 'Classification AOI');
Map.addLayer(campus, {color: 'cyan'}, 'Digitized campus', false);

var optical = ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7',
               'NDVI', 'NDBI', 'MNDWI', 'Albedo'];
function ratio(a, b, name) {
  return a.subtract(b).divide(a.add(b)).updateMask(a.add(b).neq(0)).rename(name);
}
function prep(img) {
  var qa = img.select('QA_PIXEL');
  var clean = qa.bitwiseAnd(63).eq(0).and(img.select('QA_RADSAT').eq(0));
  var sr = img.select('SR_B[2-7]').multiply(0.0000275).add(-0.2).updateMask(clean);
  var ndvi = ratio(sr.select('SR_B5'), sr.select('SR_B4'), 'NDVI');
  var ndbi = ratio(sr.select('SR_B6'), sr.select('SR_B5'), 'NDBI');
  var water = ratio(sr.select('SR_B3'), sr.select('SR_B6'), 'MNDWI');
  var albedo = sr.expression(
    '0.356*b2 + 0.130*b4 + 0.373*b5 + 0.085*b6 + 0.072*b7 - 0.0018',
    {b2: sr.select('SR_B2'), b4: sr.select('SR_B4'), b5: sr.select('SR_B5'),
     b6: sr.select('SR_B6'), b7: sr.select('SR_B7')}).rename('Albedo');
  // Optical classification need not lose pixels just because thermal data are missing.
  var thermalMask = clean.and(img.select('ST_QA').multiply(0.01).lt(3))
    .and(img.select('ST_CDIST').multiply(0.01).gt(0.2));
  var lst = img.select('ST_B10').multiply(0.00341802).add(149).subtract(273.15)
    .updateMask(thermalMask).rename('LST');
  var emis = img.select('ST_EMIS').multiply(0.0001).updateMask(thermalMask).rename('EMIS');
  return sr.addBands([ndvi, ndbi, water, albedo, lst, emis]);
}
var scenes = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
  .merge(ee.ImageCollection('LANDSAT/LC09/C02/T1_L2'))
  .filterBounds(aoi).filter(ee.Filter.eq('PROCESSING_LEVEL', 'L2SP'))
  .filterDate(YEAR + '-06-01', YEAR + '-10-01');
var composite = scenes.map(prep).median().clip(aoi);
Map.addLayer(composite, {bands: ['SR_B4', 'SR_B3', 'SR_B2'], min: 0, max: 0.3}, 'RGB');

var labels = typeof reference_polygons !== 'undefined'
  ? reference_polygons : (LABEL_ASSET ? ee.FeatureCollection(LABEL_ASSET) : null);
if (!labels) {
  print('NEXT: import/draw reference_polygons as a FeatureCollection with the five required properties. See docs/SUPERVISED_CLASSIFICATION.md.');
} else {
  var properties = ['land_cover_class', 'reference_id', 'reference_date', 'reference_source'];
  var checked = labels.filterBounds(aoi).filter(ee.Filter.notNull(properties))
    .filter(ee.Filter.inList('land_cover_class', [1, 2, 3, 4]))
    .filter(ee.Filter.stringStartsWith('reference_date', String(YEAR) + '-'));
  ee.Dictionary({total: labels.size(), valid: checked.size(),
    classes: checked.aggregate_histogram('land_cover_class'),
    scenes: scenes.size()}).evaluate(function(info, error) {
    if (error) { print('Reference audit failed:', error); return; }
    print('Reference audit:', info);
    if (!info.scenes || !info.valid || info.total !== info.valid ||
        Object.keys(info.classes).length !== 4) {
      print('STOP: need imagery, all four classes, valid labels inside the AOI, and same-year reference dates.');
      return;
    }
    var projection = ee.Image(scenes.first()).select('SR_B2').projection();
    var exportCrs = projection.crs().getInfo();
    // Label regions must not overlap. Python rejects duplicate site/year/pixel rows.
    var sampleFeatures = optical.concat(INCLUDE_THERMAL ? ['LST', 'EMIS'] : []);
    var samples = composite.select(sampleFeatures).sampleRegions({
      collection: checked, properties: properties, scale: 30,
      projection: projection, geometries: true, tileScale: 4
    }).map(function(f) {
      var xy = f.geometry().coordinates();
      return f.set({site_id: SITE_ID, year: YEAR,
        longitude: xy.get(0), latitude: xy.get(1),
        data_source: 'gee_landsat', label_source: 'manual_dated_imagery'});
    });
    Export.table.toDrive({
      collection: samples, description: SITE_ID + '_reference_pixels_' + YEAR,
      fileFormat: 'CSV', selectors: sampleFeatures.concat(properties).concat([
        'site_id', 'year', 'longitude', 'latitude', 'data_source', 'label_source'])
    });
    // Full-AOI demonstration map; training-set accuracy is deliberately not reported.
    // Run spatial validation in Python before interpreting this map as a result.
    var rf = ee.Classifier.smileRandomForest({numberOfTrees: 150, seed: 42})
      .train({features: samples, classProperty: 'land_cover_class', inputProperties: optical});
    var classified = composite.select(optical).classify(rf).rename('land_cover_class').toByte();
    Map.addLayer(classified, {min: 1, max: 4,
      palette: ['2ca02c', 'd62728', 'bcbd22', '1f77b4']}, 'RF full-AOI map — validation pending');
    Export.image.toDrive({
      image: classified, description: SITE_ID + '_rf_landcover_' + YEAR,
      region: aoi, crs: exportCrs, scale: 30, maxPixels: 1e8,
      fileFormat: 'GeoTIFF', formatOptions: {cloudOptimized: true}
    });
    // Full optical feature raster for inference with the EXACT Python-trained model.
    Export.image.toDrive({
      image: composite.select(sampleFeatures).toFloat(),
      description: SITE_ID + '_optical_features_' + YEAR,
      region: aoi, crs: exportCrs, scale: 30, maxPixels: 1e8,
      fileFormat: 'GeoTIFF'
    });
    var zones = ee.FeatureCollection([
      ee.Feature(campus, {zona: '0_tapak_penuh'}),
      ee.Feature(campus.buffer(500, 1).difference(campus, 1), {zona: '1_0-500m'}),
      ee.Feature(campus.buffer(1000, 1).difference(campus.buffer(500, 1), 1), {zona: '2_500-1000m'}),
      ee.Feature(campus.buffer(2000, 1).difference(campus.buffer(1000, 1), 1), {zona: '3_1-2km'})
    ]);
    var area = ee.Image.pixelArea().divide(10000).rename('area_ha').addBands(classified);
    var areas = area.reduceRegions({
      collection: zones, reducer: ee.Reducer.sum().group({groupField: 1, groupName: 'class_id'}),
      scale: 30, crs: projection, tileScale: 4
    }).map(function(f) { return f.set({site_id: SITE_ID, year: YEAR}); });
    Export.table.toDrive({collection: areas,
      description: SITE_ID + '_rf_zonal_area_' + YEAR, fileFormat: 'GeoJSON'});
    print('Export tasks created. Python spatial validation remains required; these are mapped class areas, not error-adjusted estimates.');
  });
}

