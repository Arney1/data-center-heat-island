/*****************************************************************
 * RISET LENGKAP: SUHU PERMUKAAN & TUTUPAN LAHAN PUSAT DATA
 * Lokasi Studi: AWS PDX Bombing Campus (Boardman, Oregon)
 * Sensor: Landsat 8 & 9 Collection 2 Level-2 (L2SP)
 * 
 * Mencakup Tahap 1 hingga Tahap 13 (Tingkat A, B, dan C)
 * Menggunakan sistem antrean (queue) ter-evaluasi untuk mencegah 
 * "Too many concurrent aggregations" di Code Editor.
 *****************************************************************/

// ================= 0. GEOMETRI & PARAMETER ======================
// 1. Batas Luar Tapak Kampus (Campus Fence Line) - Digitasi Presisi
var campus_1 = ee.Geometry.Polygon([
  [[-119.64171195208215, 45.81800973804475],
   [-119.63429296194695, 45.8180321700963],
   [-119.63383778657992, 45.81812409215994],
   [-119.62763950444914, 45.81813904683127],
   [-119.62761412100413, 45.81829961862225],
   [-119.62517331080058, 45.81832578921197],
   [-119.6251947684727,  45.82055398288432],
   [-119.62525404980258, 45.820627992663724],
   [-119.62750174095706, 45.82087099464729],
   [-119.62901450684146, 45.82087473313103],
   [-119.63007129719333, 45.82077753247144],
   [-119.63051117947177, 45.820598084653994],
   [-119.63057555248812, 45.82051583754439],
   [-119.63146068146304, 45.820508360528414],
   [-119.63154114773349, 45.82058686914621],
   [-119.63215805580691, 45.820762578508734],
   [-119.63524796059207, 45.82083360979578],
   [-119.64057482769564, 45.82081491736061],
   [-119.64174963524417, 45.82077005549056],
   [-119.64171195208215, 45.81800973804475]]
]);

// 2. Poligon 4 Gedung Pusat Data Terpisah (4 Data Halls MultiPolygon)
var only_yellows = ee.Geometry.MultiPolygon([
  // Gedung Barat Laut (NW)
  [[[-119.63834382441334, 45.81937363830602],
    [-119.63423468020252, 45.81935868396625],
    [-119.63425613787464, 45.820330707696094],
    [-119.63834382441334, 45.82030827657055],
    [-119.63834382441334, 45.81937363830602]]],
  // Gedung Timur Laut (NE)
  [[[-119.63411666300587, 45.81938111547438],
    [-119.629996789959,   45.81940354697348],
    [-119.63002897646717, 45.82036061584945],
    [-119.63411666300587, 45.82032323065526],
    [-119.63411666300587, 45.81938111547438]]],
  // Gedung Barat Daya (SW)
  [[[-119.6383545532494,  45.81838664326721],
    [-119.63425613787464, 45.81838664326721],
    [-119.63424540903858, 45.819321298099304],
    [-119.63837601092152, 45.81929138938767],
    [-119.6383545532494,  45.81838664326721]]],
  // Gedung Timur Daya (SE)
  [[[-119.63411666300587, 45.81837916596529],
    [-119.63001824763111, 45.81840907516693],
    [-119.63003970530323, 45.81935868396625],
    [-119.63410593416981, 45.81929886656709],
    [-119.63411666300587, 45.81837916596529]]]
]);

var campus = campus_1;                                  // Batas luar tapak kampus (fence line)
var bangunan = only_yellows.intersection(campus, 1);    // Poligon bangunan di dalam tapak
var sisaTapak = campus.difference(bangunan, 1);         // Area tapak di luar bangunan
var bangunanDalam = bangunan.buffer(-15, 1);            // Piksel murni bangunan (tanpa batas campur)

var haCampus = campus.area(1).divide(10000);
var haBangunan = bangunan.area(1).divide(10000);
print('--- LUAS TAPAK KAMPUS ---');
print('Luas Total Kampus (ha):', haCampus);
print('Luas Bangunan Saja (ha):', haBangunan);
print('Luas Area Non-Bangunan (ha):', haCampus.subtract(haBangunan));
print('Persentase Bangunan (%):', haBangunan.divide(haCampus).multiply(100));

// Periode Pengamatan
var YEARS = [];
for (var yy = 2013; yy <= 2026; yy++) { YEARS.push(yy); }
var BULAN_AWAL = 6, BULAN_AKHIR = 9;   // Jendela musim panas/kering (Juni - September)
var ST_QA_MAX = 3.0;                   // Batas ketidakpastian suhu maksimum (Kelvin)
var CDIST_MIN_KM = 0.2;                // Jarak minimum ke awan (km)
var FV_MIN = 0.7;                      // Fraksi piksel valid minimum per citra
var THR_NDBI = -0.1;                   // Ambang awal NDBI
var THR_NDVI_BUILT = 0.2;              // Ambang batas vegetasi vs terbangun

// Kronologi AWS PDX:
// Pra-konstruksi: 2019-2021 | Transisi/Konstruksi: 2022-2024 | Pasca-konstruksi/Operasional: 2025-2026
var PRE_TAHUN  = [2019, 2020, 2021];
var POST_TAHUN = [2025, 2026];
var K_TAHUN = 2025;                    // Tahun acuan untuk K-means dan kalibrasi

// Sakelar Modul (Semua diaktifkan secara berurutan)
var RUN_TERSEDIA   = true;   // Tahap 2 & Gerbang G3: Ketersediaan citra bersih
var RUN_SERI       = true;   // Tahap 3 & 9: Runtun waktu tahunan per zona
var RUN_BUILT      = true;   // Tahap 6: Peta tahun mulai terbangun persisten
var RUN_KALIBRASI  = true;   // Tahap 5: Kalibrasi ambang spektral & akurasi
var RUN_PETA_LST   = true;   // Tahap 7, 8, 10: Peta LST, anomali, gradien, & audit emisivitas
var RUN_KMEANS     = true;   // Tahap 4: Clustering tanpa supervisi (k = 5, 10, 20)
var RUN_TREN       = true;   // Tahap 9: Analisis tren piksel (Sen's Slope & Mann-Kendall)
var RUN_REGRESI    = true;   // Tahap 11: Regresi spasial kovariat (NDVI, NDBI, elevasi, albedo, jarak)
var RUN_IKTL       = true;   // Tahap 12: Indeks Koinsidensi Termal-Lahan & ablasi
var RUN_PEMBANDING = true;   // Tahap 13: Pembanding berpasangan (Difference-in-Differences)

// ================= 1. ZONA SPASIAL & AREA REFERENSI =============
var aoi = campus.buffer(2500);
var z1 = campus.buffer(500).difference(campus);
var z2 = campus.buffer(1000).difference(campus.buffer(500));
var z3 = campus.buffer(2000).difference(campus.buffer(1000));

var zonaFC = ee.FeatureCollection([
  ee.Feature(campus, {zona: '0_tapak_penuh'}),
  ee.Feature(bangunan, {zona: '0a_bangunan'}),
  ee.Feature(sisaTapak, {zona: '0b_sisa_tapak'}),
  ee.Feature(z1, {zona: '1_0-500m'}),
  ee.Feature(z2, {zona: '2_500-1000m'}),
  ee.Feature(z3, {zona: '3_1-2km'})
]);

Map.setOptions('SATELLITE');
Map.centerObject(campus, 14);
Map.addLayer(zonaFC.style({color: 'yellow', fillColor: '00000000', width: 1}), {}, 'Zona Cincin Jarak');
Map.addLayer(campus, {color: 'cyan'}, 'Tapak Kampus Penuh', false);
Map.addLayer(ee.FeatureCollection([ee.Feature(bangunan)]).style({color: 'red', fillColor: 'ff000033', width: 2}), {}, 'Bangunan Kampus (4 Data Halls)');

// Area Referensi Regional: Cincin 5-12 km, kelas lahan pertanian (WorldCover class 40), lereng < 3 derajat
var wc = ee.ImageCollection('ESA/WorldCover/v200').first().select('Map');
var dem = ee.Image('USGS/SRTMGL1_003').select('elevation');
var lereng = ee.Terrain.slope(dem);
var refMask = wc.eq(40).and(lereng.lt(3));
var refGeom = campus.buffer(12000).difference(campus.buffer(5000));
Map.addLayer(refMask.updateMask(refMask).clip(refGeom), {palette: ['00cc66']}, 'Area Referensi Pertanian', false);

// Area Pembanding Berpasangan (Tingkat C - Fasilitas Non-Pusat Data di kawasan industri terdekat)
var pembandingGeom = ee.Geometry.Point([-119.6975, 45.8361]).buffer(400); // Plot industri/logistik Boardman
Map.addLayer(pembandingGeom, {color: 'magenta'}, 'Kontrol Pembanding Berpasangan (DiD)', false);

// ================= 2. PREPROCESSING & PENGAYAAN BAND ============
var L8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2');
var L9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2');
var L89 = L8.merge(L9)
    .filterBounds(campus.buffer(12000))
    .filter(ee.Filter.eq('PROCESSING_LEVEL', 'L2SP'));

function prep(img) {
  img = ee.Image(img);
  var qa = img.select('QA_PIXEL');
  var ok = qa.bitwiseAnd(1 << 1).eq(0)                        // Dilated cloud
      .and(qa.bitwiseAnd(1 << 3).eq(0))                       // Cloud
      .and(qa.bitwiseAnd(1 << 4).eq(0))                       // Cloud shadow
      .and(img.select('ST_QA').multiply(0.01).lt(ST_QA_MAX))  // Ketidakpastian suhu
      .and(img.select('ST_CDIST').multiply(0.01).gt(CDIST_MIN_KM)); // Jarak ke awan

  var sr = img.select('SR_B.').multiply(0.0000275).add(-0.2);
  var lst = img.select('ST_B10').multiply(0.00341802).add(149.0).subtract(273.15).rename('LST');
  var emis = img.select('ST_EMIS').multiply(0.0001).rename('EMIS');
  var ndvi = sr.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI');
  var ndbi = sr.normalizedDifference(['SR_B6', 'SR_B5']).rename('NDBI');
  var mndwi = sr.normalizedDifference(['SR_B3', 'SR_B6']).rename('MNDWI');
  
  // Broadband Surface Albedo (Formula Liang 2001 / Tasumi et al. 2008)
  var albedo = sr.expression(
    '0.356 * B2 + 0.130 * B4 + 0.373 * B5 + 0.085 * B6 + 0.072 * B7 - 0.0018',
    {
      'B2': sr.select('SR_B2'), 'B4': sr.select('SR_B4'), 'B5': sr.select('SR_B5'),
      'B6': sr.select('SR_B6'), 'B7': sr.select('SR_B7')
    }
  ).rename('albedo');

  return ee.Image(ee.Image.cat([lst, emis, ndvi, ndbi, mndwi, albedo])
      .updateMask(ok)
      .copyProperties(img, ['system:time_start']));
}

function seleksi(y) {
  return L89.filter(ee.Filter.calendarRange(y, y, 'year'))
      .filter(ee.Filter.calendarRange(BULAN_AWAL, BULAN_AKHIR, 'month'));
}

function komposRaw(y) {
  var col = seleksi(y).map(prep);
  var med = col.median();
  var n = col.select('LST').count().rename('N');
  var fv = med.select('LST').mask().rename('fv');
  return ee.Image.cat([med, n, fv]).toFloat().set('tahun', y);
}

var RAW = {};
YEARS.forEach(function (y) { RAW[y] = komposRaw(y); });

// Sistem Antrean Eksekusi Berurutan
var antrian = [];
function tambah(fn) { antrian.push(fn); }
function lanjut() {
  if (antrian.length === 0) { print('=== SEMUA TAHAP ANALISIS SELESAI DIEKSEKUSI ==='); return; }
  var fn = antrian.shift();
  fn(lanjut);
}

// ================= 3. PEMROSESAN UTAMA ==========================
function utama(ref) {
  var KOMP = {};
  YEARS.forEach(function (y) {
    var r = ref['y' + y];
    if (r === null || r === undefined) { r = 0; }
    var c = RAW[y];
    KOMP[y] = c.addBands(c.select('LST').subtract(r).rename('LSTanom'))
        .toFloat().set('tahun', y).set('refLST', r);
  });

  function gabung(arr) {
    return ee.ImageCollection.fromImages(arr.map(function (y) { return KOMP[y]; })).median();
  }
  var pre = gabung(PRE_TAHUN);
  var post = gabung(POST_TAHUN);
  var dLSTanom = post.select('LSTanom').subtract(pre.select('LSTanom')).rename('dLSTanom');
  var dLST  = post.select('LST').subtract(pre.select('LST')).rename('dLST');
  var dNDVI = post.select('NDVI').subtract(pre.select('NDVI')).rename('dNDVI');
  var dNDBI = post.select('NDBI').subtract(pre.select('NDBI')).rename('dNDBI');
  var dEMIS = post.select('EMIS').subtract(pre.select('EMIS')).rename('dEMIS');
  var tanpaAir = pre.select('MNDWI').lt(0).and(post.select('MNDWI').lt(0));

  function builtMask(c) {
    return c.select('NDBI').gt(THR_NDBI)
        .and(c.select('NDVI').lt(THR_NDVI_BUILT))
        .and(c.select('MNDWI').lt(0))
        .unmask(0).rename('built');
  }

  // --- TAHAP 2: KETERSEDIAAN CITRA BERSIH (GERBANG G3) ---
  if (RUN_TERSEDIA) {
    tambah(function (selesai) {
      var scenes = L89.filterBounds(campus)
          .filter(ee.Filter.calendarRange(BULAN_AWAL, BULAN_AKHIR, 'month'))
          .filter(ee.Filter.calendarRange(YEARS[0], YEARS[YEARS.length - 1], 'year'));
      var fcScene = scenes.map(function (img) {
        var f = ee.Image(prep(img)).select('LST').mask().reduceRegion({
          reducer: ee.Reducer.mean(), geometry: campus, scale: 30, maxPixels: 1e9
        }).get('LST');
        return ee.Feature(ee.Geometry.Point([0, 0]), {
          tahun: ee.Date(img.get('system:time_start')).get('year'), fv: f
        });
      });
      ee.Dictionary({
        nScene: fcScene.aggregate_histogram('tahun'),
        nBersih: fcScene.filter(ee.Filter.gte('fv', FV_MIN)).aggregate_histogram('tahun')
      }).evaluate(function (d, err) {
        if (err) { print('Tahap 1 Error:', err); selesai(); return; }
        var chartData = [['Tahun', 'Total Scene', 'Scene Bersih (>= 70%)']];
        var outObj = {};
        YEARS.forEach(function (y) {
          var tot = d.nScene[y] || 0;
          var ber = d.nBersih[y] || 0;
          chartData.push([String(y), tot, ber]);
          outObj[y] = {total_scene: tot, scene_bersih: ber};
        });
        print('1) Gerbang G3: Ketersediaan Citra Bersih (Juni-September):', outObj);
        print(ui.Chart(chartData).setChartType('ColumnChart').setOptions({
          title: 'Ketersediaan Citra Per Tahun (Tapak Kampus)',
          hAxis: {title: 'Tahun'},
          vAxis: {title: 'Jumlah Citra'}
        }));
        selesai();
      });
    });
  }

  // --- TAHAP 3 & 9: SERI WAKTU TAHUNAN PER ZONA ---
  if (RUN_SERI) {
    tambah(function (selesai) {
      print('2) Suhu Referensi Regional LST Tahunan (Lahan Pertanian):', ref);

      var listTahunImg = YEARS.map(function (y) {
        var im = KOMP[y];
        return im.select(['LST', 'LSTanom', 'EMIS', 'NDVI', 'NDBI'])
            .updateMask(im.select('MNDWI').lt(0))
            .select(
              ['LST', 'LSTanom', 'EMIS', 'NDVI', 'NDBI'],
              ['LST_' + y, 'LSTanom_' + y, 'EMIS_' + y, 'NDVI_' + y, 'NDBI_' + y]
            );
      });
      var stackedZona = ee.Image.cat(listTahunImg);

      var zonaStats = stackedZona.reduceRegions({
        collection: zonaFC,
        reducer: ee.Reducer.mean(),
        scale: 30,
        tileScale: 4
      });

      zonaStats.evaluate(function (r, err) {
        if (err) { print('Tahap 2 Error:', err); selesai(); return; }
        var rows = [];
        r.features.forEach(function (f) {
          var props = f.properties;
          var zName = props.zona;
          YEARS.forEach(function (y) {
            rows.push(ee.Feature(ee.Geometry.Point([0, 0]), {
              tahun: y,
              zona: zName,
              LST: props['LST_' + y],
              LSTanom: props['LSTanom_' + y],
              EMIS: props['EMIS_' + y],
              NDVI: props['NDVI_' + y],
              NDBI: props['NDBI_' + y]
            }));
          });
        });
        var tabel = ee.FeatureCollection(rows);
        ['LSTanom', 'LST', 'NDVI', 'NDBI'].forEach(function (b) {
          print(ui.Chart.feature.groups(tabel, 'tahun', b, 'zona')
              .setChartType('LineChart')
              .setOptions({title: 'Dinamika ' + b + ' Per Zona (2013-2026)', hAxis: {format: '####'}, pointSize: 3}));
        });
        selesai();
      });
    });
  }

  // --- TAHAP 6: PETA TAHUN MULAI TERBANGUN (PERSISTENT SPRAWL) ---
  if (RUN_BUILT) {
    tambah(function (selesai) {
      var builtImgs = YEARS.map(function (y) { return builtMask(KOMP[y]); });
      var persist = null;
      var mulai = ee.Image.constant(0).toInt16().rename('mulai');
      for (var i = YEARS.length - 1; i >= 0; i--) {
        persist = (persist === null) ? builtImgs[i] : builtImgs[i].and(persist);
        mulai = mulai.where(persist, YEARS[i]);
      }
      Map.addLayer(mulai.updateMask(mulai.gt(0)).clip(aoi),
          {min: 2013, max: 2026, palette: ['red', 'orange', 'yellow', 'green', 'blue']},
          'Peta Tahun Mulai Terbangun (Persisten)');

      var pixelHa = ee.Image.pixelArea().divide(10000);
      var haStack = ee.Image.cat(YEARS.map(function (y) {
        return builtMask(KOMP[y]).multiply(pixelHa).rename('ha_' + y);
      }));

      var redBldg = haStack.reduceRegion({
        reducer: ee.Reducer.sum(),
        geometry: bangunan,
        scale: 30,
        maxPixels: 1e9,
        tileScale: 4
      });

      var redRest = haStack.reduceRegion({
        reducer: ee.Reducer.sum(),
        geometry: sisaTapak,
        scale: 30,
        maxPixels: 1e9,
        tileScale: 4
      });

      ee.Dictionary({bangunan: redBldg, sisaTapak: redRest}).evaluate(function (res, err) {
        if (err) { print('Tahap 3 Error:', err); selesai(); return; }
        var rows = [];
        YEARS.forEach(function (y) {
          rows.push(ee.Feature(ee.Geometry.Point([0, 0]), {
            tahun: y,
            zona: 'bangunan',
            ha: res.bangunan['ha_' + y]
          }));
          rows.push(ee.Feature(ee.Geometry.Point([0, 0]), {
            tahun: y,
            zona: 'sisa_tapak',
            ha: res.sisaTapak['ha_' + y]
          }));
        });
        var tabel = ee.FeatureCollection(rows);
        print('3) Lintasan Luas Lahan Terbangun (ha) di Dalam Tapak Kampus');
        print(ui.Chart.feature.groups(tabel, 'tahun', 'ha', 'zona').setChartType('LineChart')
            .setOptions({title: 'Ekspansi Fisik Bangunan vs Area Tapak Lainnya (ha)', hAxis: {format: '####'}}));
        selesai();
      });
    });
  }

  // --- TAHAP 5: KALIBRASI AMBANG & AKURASI ---
  if (RUN_KALIBRASI) {
    tambah(function (selesai) {
      var cA = KOMP[K_TAHUN].select(['NDVI', 'NDBI']);
      var q = {
        bangunan: cA.reduceRegion({reducer: ee.Reducer.median(), geometry: bangunanDalam, scale: 30, maxPixels: 1e9, tileScale: 4}),
        referensi: cA.updateMask(refMask).reduceRegion({reducer: ee.Reducer.median(), geometry: refGeom, scale: 60, maxPixels: 1e9, bestEffort: true, tileScale: 4})
      };
      ee.Dictionary(q).evaluate(function (d, err) {
        if (err) { print('Tahap 4 Error:', err); selesai(); return; }
        print('4) Kalibrasi Ambang: Median NDBI Bangunan = ' + d.bangunan.NDBI.toFixed(3) + ', Referensi = ' + d.referensi.NDBI.toFixed(3));
        print('Rekomendasi Ambang NDBI Baru:', (d.bangunan.NDBI + d.referensi.NDBI) / 2);
        selesai();
      });
    });
  }

  // --- TAHAP 7, 8, & 10: PETA LST, ANOMALI, GRADIEN, & AUDIT EMISIVITAS ---
  if (RUN_PETA_LST) {
    tambah(function (selesai) {
      var palLST = ['blue', 'cyan', 'yellow', 'orange', 'red'];
      var palDiv = ['0000ff', 'ffffff', 'ff0000'];
      Map.addLayer(pre.select('LST').clip(aoi), {min: 25, max: 48, palette: palLST}, 'LST Pra-Konstruksi (C)', false);
      Map.addLayer(post.select('LST').clip(aoi), {min: 25, max: 48, palette: palLST}, 'LST Pasca-Konstruksi (C)');
      Map.addLayer(dLSTanom.updateMask(tanpaAir).clip(aoi), {min: -4, max: 4, palette: palDiv}, 'Perubahan Anomali LST (Pasca - Pra)');

      var stackZona = ee.Image.cat([
        pre.select('LSTanom').rename('anom_pre'),
        post.select('LSTanom').rename('anom_post'),
        dLSTanom, dNDVI, dNDBI, dEMIS
      ]).updateMask(tanpaAir);

      stackZona.reduceRegions({collection: zonaFC, reducer: ee.Reducer.mean(), scale: 30, tileScale: 4}).evaluate(function (r, err) {
        if (err) { print('Tahap 5 Error:', err); selesai(); return; }
        var tabel = ee.FeatureCollection(r.features.map(function(f) {
          return ee.Feature(ee.Geometry.Point([0, 0]), f.properties);
        }));
        print('5) Rerata Perubahan Anomali Termal Per Zona', tabel);
        print(ui.Chart.feature.byFeature(tabel, 'zona', ['anom_pre', 'anom_post'])
            .setChartType('ColumnChart')
            .setOptions({title: 'Perbandingan Anomali LST Sebelum vs Sesudah Konstruksi'}));

        var getZ = function (zName, p) {
          for (var i = 0; i < r.features.length; i++) {
            if (r.features[i].properties.zona === zName) return r.features[i].properties[p];
          }
          return 0;
        };
        var Gpre = (getZ('3_1-2km', 'anom_pre') - getZ('1_0-500m', 'anom_pre')) / 1.25;
        var Gpost = (getZ('3_1-2km', 'anom_post') - getZ('1_0-500m', 'anom_post')) / 1.25;
        print('Gradien Spasial Pra-Konstruksi (C/km):', Gpre);
        print('Gradien Spasial Pasca-Konstruksi (C/km):', Gpost);
        print('Perubahan Gradien Spasial (Delta G):', Gpost - Gpre);

        // Audit Emisivitas ASTER GED
        var audit = ee.Image.cat([dNDVI, dEMIS, dLST]).updateMask(tanpaAir);
        audit.sample({region: aoi, scale: 30, numPixels: 2000, seed: 11, tileScale: 4}).evaluate(function (s, err2) {
          if (err2) { selesai(); return; }
          var fs = ee.FeatureCollection(s.features.map(function(f) {
            return ee.Feature(ee.Geometry.Point([0, 0]), f.properties);
          }));
          print(ui.Chart.feature.byFeature(fs, 'dNDVI', ['dEMIS']).setChartType('ScatterChart')
              .setOptions({title: 'Audit Emisivitas: Delta Emisivitas vs Delta NDVI', pointSize: 2}));
          print(ui.Chart.feature.byFeature(fs, 'dEMIS', ['dLST']).setChartType('ScatterChart')
              .setOptions({title: 'Audit Artefak: Delta LST vs Delta Emisivitas', pointSize: 2}));
          selesai();
        });
      });
    });
  }

  // --- TAHAP 4: K-MEANS CLUSTERING (k = 5, 10, 20) ---
  if (RUN_KMEANS) {
    tambah(function (selesai) {
      var cK = KOMP[K_TAHUN].select(['NDVI', 'NDBI', 'MNDWI']);
      var latih = cK.sample({region: aoi, scale: 30, numPixels: 5000, seed: 42, tileScale: 4});
      var q = {};
      [5, 10, 20].forEach(function (k) {
        var klaster = ee.Clusterer.wekaKMeans(k).train(latih);
        var hasil = cK.cluster(klaster).clip(aoi);
        Map.addLayer(hasil.randomVisualizer(), {}, 'KMeans k=' + k, false);
        var area = ee.Image.pixelArea().divide(10000).addBands(hasil);
        q['k' + k + '_kampus'] = area.reduceRegion({
          reducer: ee.Reducer.sum().group({groupField: 1, groupName: 'klaster'}),
          geometry: campus, scale: 30, maxPixels: 1e9, tileScale: 4
        });
      });
      ee.Dictionary(q).evaluate(function (d, err) {
        if (err) { print('Tahap 6 Error:', err); selesai(); return; }
        print('6) Proporsi Luas Kluster K-Means di Dalam Kampus (k = 5, 10, 20):', d);
        selesai();
      });
    });
  }

  // --- TAHAP 9: TREN PIKSEL (SEN'S SLOPE & MANN-KENDALL) ---
  if (RUN_TREN) {
    tambah(function (selesai) {
      var seri = ee.ImageCollection.fromImages(YEARS.map(function (y) {
        var tt = ee.Image.constant(y).float().rename('t');
        return ee.Image.cat([tt, KOMP[y].select('LSTanom')]).toFloat();
      }));
      var nValid = seri.select('LSTanom').count().clip(aoi);
      Map.addLayer(nValid, {min: 0, max: 14, palette: ['white', 'blue']}, 'Jumlah Tahun Valid', false);
      
      var sen = seri.select(['t', 'LSTanom']).reduce(ee.Reducer.sensSlope());
      var mk  = seri.select(['t', 'LSTanom']).reduce(ee.Reducer.kendallsCorrelation(2));
      var palTren = ['#0000ff', '#ffffff', '#ff0000'];
      Map.addLayer(sen.select('slope').updateMask(nValid.gte(5)).clip(aoi),
          {min: -0.3, max: 0.3, palette: palTren}, 'Sen\'s Slope Tren Anomali (C/tahun)');
      Map.addLayer(mk.select('tau').updateMask(nValid.gte(5)).clip(aoi),
          {min: -0.5, max: 0.5, palette: palTren}, 'Mann-Kendall Tau', false);
      print('7) Analisis Tren Piksel Non-Parametrik Berhasil Dipetakan.');
      selesai();
    });
  }

  // --- TAHAP 11: REGRESI KOVARIAT MULTIVARIAT (SEBELUM vs SESUDAH) ---
  if (RUN_REGRESI) {
    tambah(function (selesai) {
      var regGeom = aoi.difference(campus);
      var distImg = ee.FeatureCollection([ee.Feature(campus)]).distance(10000).divide(1000).rename('dist_km');

      var fitRegresi = function (im, namaPeriode) {
        var stack = ee.Image.cat([
          ee.Image.constant(1).rename('konstanta'),
          im.select('NDVI'),
          im.select('NDBI'),
          dem.rename('elevasi'),
          im.select('albedo'),
          distImg,
          im.select('LSTanom')
        ]).updateMask(tanpaAir);

        var reg = stack.reduceRegion({
          reducer: ee.Reducer.linearRegression(6, 1),
          geometry: regGeom,
          scale: 100,
          maxPixels: 1e9,
          tileScale: 4
        });
        return ee.Dictionary({
          periode: namaPeriode,
          koefisien: ee.Array(reg.get('coefficients')).toList().flatten()
        });
      };

      ee.Dictionary({
        pre: fitRegresi(pre, 'Pra-Konstruksi'),
        post: fitRegresi(post, 'Pasca-Konstruksi')
      }).evaluate(function (d, err) {
        if (err) { print('Tahap 8 Error:', err); selesai(); return; }
        var formatKoef = function (arr) {
          return {
            b0_Intercept: arr[0], b1_NDVI: arr[1], b2_NDBI: arr[2],
            b3_Elevasi: arr[3], b4_Albedo: arr[4], b5_Jarak_km: arr[5]
          };
        };
        print('8) Model Regresi Kovariat Pra-Konstruksi:', formatKoef(d.pre.koefisien));
        print('8) Model Regresi Kovariat Pasca-Konstruksi:', formatKoef(d.post.koefisien));
        print('Perubahan Efek Jarak (b5 Pasca - Pra):', (d.post.koefisien[5] - d.pre.koefisien[5]));
        selesai();
      });
    });
  }

  // --- TAHAP 12: INDEKS KOINSIDENSI TERMAL-LAHAN (IKTL) & ABLASI ---
  if (RUN_IKTL) {
    tambah(function (selesai) {
      var P30 = L8.filterBounds(campus).first().select('SR_B1').projection();
      var agg100 = function (img) {
        return img.setDefaultProjection(P30)
            .reduceResolution({reducer: ee.Reducer.mean(), maxPixels: 64})
            .reproject({crs: P30, scale: 100});
      };

      var preBuilt = builtMask(pre), postBuilt = builtMask(post);
      var preVeg = pre.select('NDVI').gt(0.3);
      var v4 = ee.Image(1)
          .where(postBuilt.and(preBuilt.not()).and(preVeg), 5)
          .where(postBuilt.and(preBuilt.not()).and(preVeg.not()), 3)
          .rename('v4');

      var V0 = ee.Image.cat([dLSTanom.rename('v1'), dNDVI.multiply(-1).rename('v2'), dNDBI.rename('v3')]).updateMask(tanpaAir);
      var Vagg = agg100(V0);
      var v4agg = agg100(v4).round().rename('v4').updateMask(Vagg.select('v1').mask());

      var pct = function (b) {
        return Vagg.select(b).updateMask(refMask).reduceRegion({
          reducer: ee.Reducer.percentile([50, 75, 90, 97]), geometry: refGeom,
          scale: 100, maxPixels: 1e9, bestEffort: true, tileScale: 4
        });
      };

      ee.Dictionary({v1: pct('v1'), v2: pct('v2'), v3: pct('v3')}).evaluate(function (d, err) {
        if (err) { print('Tahap 9 Error:', err); selesai(); return; }
        var cut = function (dict, suf) {
          var ks = Object.keys(dict).filter(function (s) { return s.slice(-suf.length) === suf; });
          return dict[ks[0]];
        };
        var harkat = function (b) {
          var x = Vagg.select(b);
          var dd = d[b];
          return ee.Image(1)
              .where(x.gt(cut(dd, 'p50')), 2)
              .where(x.gt(cut(dd, 'p75')), 3)
              .where(x.gt(cut(dd, 'p90')), 4)
              .where(x.gt(cut(dd, 'p97')), 5)
              .updateMask(x.mask()).rename(b + '_h');
        };

        var H = ee.Image.cat([harkat('v1'), harkat('v2'), harkat('v3'), v4agg]);
        var iktl = function (bList) {
          var m = H.select(bList).reduce(ee.Reducer.mean());
          return ee.Image(1).where(m.gte(2), 2).where(m.gte(2.75), 3).where(m.gte(3.5), 4).where(m.gte(4.25), 5).updateMask(m.mask()).rename('IKTL');
        };

        var varian = {
          'Penuh (V1-V4)': ['v1_h', 'v2_h', 'v3_h', 'v4'],
          'Tanpa V1 (Termal)': ['v2_h', 'v3_h', 'v4'],
          'Tanpa V2+V3 (Permukaan)': ['v1_h', 'v4'],
          'Tanpa V4 (Konversi)': ['v1_h', 'v2_h', 'v3_h']
        };

        var q = {};
        Object.keys(varian).forEach(function (k) {
          var im = iktl(varian[k]).clip(aoi);
          Map.addLayer(im, {min: 1, max: 5, palette: ['2b83ba', 'abdda4', 'ffffbf', 'fdae61', 'd7191c']}, 'IKTL ' + k, k === 'Penuh (V1-V4)');
          q[k] = ee.Image.pixelArea().divide(10000).addBands(im).reduceRegion({
            reducer: ee.Reducer.sum().group({groupField: 1, groupName: 'kelas'}),
            geometry: aoi, scale: 100, maxPixels: 1e9, tileScale: 4
          });
        });
        ee.Dictionary(q).evaluate(function (res, err2) {
          if (err2) { selesai(); return; }
          print('9) Distribusi Luas Kelas IKTL & Analisis Sensitivitas Ablasi (ha):', res);
          selesai();
        });
      });
    });
  }

  // --- TAHAP 13: PEMBANDING BERPASANGAN (DIFFERENCE-IN-DIFFERENCES) ---
  if (RUN_PEMBANDING) {
    tambah(function (selesai) {
      var dLST_kampus = post.select('LST').subtract(pre.select('LST')).reduceRegion({
        reducer: ee.Reducer.mean(), geometry: campus, scale: 30, maxPixels: 1e9, tileScale: 4
      }).get('LST');

      var dLST_kontrol = post.select('LST').subtract(pre.select('LST')).reduceRegion({
        reducer: ee.Reducer.mean(), geometry: pembandingGeom, scale: 30, maxPixels: 1e9, tileScale: 4
      }).get('LST');

      ee.Dictionary({
        delta_T_kampus: dLST_kampus,
        delta_T_pembanding: dLST_kontrol
      }).evaluate(function (d, err) {
        if (err) { print('Tahap 10 Error:', err); selesai(); return; }
        var DiD = d.delta_T_kampus - d.delta_T_pembanding;
        print('10) Evaluasi DiD (Tingkat C):');
        print('    Delta LST Kampus (Pasca - Pra): ' + d.delta_T_kampus.toFixed(3) + ' C');
        print('    Delta LST Pembanding Non-DC: ' + d.delta_T_pembanding.toFixed(3) + ' C');
        print('    Estimator Efek Bersih Relatif (DiD): ' + DiD.toFixed(3) + ' C');
        selesai();
      });
    });
  }

  lanjut();
}

// ================= INISIASI: PENGHITUNGAN SUHU REFERENSI =========
var stackLST = ee.Image.cat(YEARS.map(function (y) { return RAW[y].select('LST').rename('y' + y); }));
print('Memulai pra-pemrosesan & menghitung suhu referensi regional...');
stackLST.updateMask(refMask).reduceRegion({
  reducer: ee.Reducer.median(), geometry: refGeom, scale: 60, maxPixels: 1e9, bestEffort: true, tileScale: 4
}).evaluate(function (ref, err) {
  if (err) { print('Kesalahan Referensi:', err); return; }
  utama(ref);
});
