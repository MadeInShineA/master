var geometry = 
    ee.Geometry.Polygon(
        [[[36.12400044795963, 36.24467594227881],
          [36.12400044795963, 36.1920492069449],
          [36.18940343257877, 36.1920492069449],
          [36.18940343257877, 36.24467594227881]]], null, false);

/**
 * Function to mask clouds using the Sentinel-2 QA band
 * @param {ee.Image} image Sentinel-2 image
 * @return {ee.Image} cloud masked Sentinel-2 image
 */
function maskS2clouds(image) {
  var qa = image.select('QA60');

  // Bits 10 and 11 are clouds and cirrus, respectively.
  var cloudBitMask = 1 << 10;
  var cirrusBitMask = 1 << 11;

  // Both flags should be set to zero, indicating clear conditions.
  var mask = qa.bitwiseAnd(cloudBitMask).eq(0)
      .and(qa.bitwiseAnd(cirrusBitMask).eq(0));

  return image.updateMask(mask).divide(10000);
}

var zone_name = 'antioche';

for (var year=2022; year < 2024; year++) {
  print(""+year);

  var dataset = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                    .filterDate(""+year+'-03-01', ""+year+'-04-30')
                    // Pre-filter to get less cloudy granules.
                    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',20))
                    .map(maskS2clouds);
  
  var image = dataset.select(['B4', 'B3', 'B2']).mean().clip(geometry);
  
  print(image);
  
  // Export the image, specifying scale and region.
  Export.image.toDrive({
    image: image,
    description: 'sentinel_'+zone_name,
    scale: 10,
    region: geometry,
    fileNamePrefix: zone_name+'_'+year,
    folder: 'sentinel'
  });
  
}

