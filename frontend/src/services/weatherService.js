const WX_CODE_MAP = {
  0: { desc: 'Clear Sky', icon: '☀️' },
  1: { desc: 'Mainly Clear', icon: '🌤️' },
  2: { desc: 'Partly Cloudy', icon: '⛅' },
  3: { desc: 'Overcast', icon: '☁️' },
  45: { desc: 'Foggy Mist', icon: '🌫️' },
  48: { desc: 'Depositing Rime Fog', icon: '🌫️' },
  51: { desc: 'Light Drizzle', icon: '🌦️' },
  53: { desc: 'Moderate Drizzle', icon: '🌦️' },
  55: { desc: 'Dense Drizzle', icon: '🌧️' },
  61: { desc: 'Slight Rain', icon: '🌧️' },
  63: { desc: 'Moderate Rain', icon: '🌧️' },
  65: { desc: 'Heavy Rain', icon: '🌧️' },
  71: { desc: 'Slight Snow Fall', icon: '🌨️' },
  73: { desc: 'Moderate Snow Fall', icon: '🌨️' },
  75: { desc: 'Heavy Snow Fall', icon: '❄️' },
  80: { desc: 'Rain Showers', icon: '🌦️' },
  81: { desc: 'Moderate Showers', icon: '🌦️' },
  82: { desc: 'Violent Showers', icon: '⛈️' },
  95: { desc: 'Thunderstorm', icon: '⛈️' },
};

/**
 * Fetches real-time live weather for any destination using Open-Meteo API
 * (Free, reliable, no API key required).
 * @param {string} destinationName
 */
export async function getLiveWeather(destinationName) {
  if (!destinationName) return null;

  try {
    // 1. Geocoding
    const geoUrl = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(
      destinationName.trim()
    )}&count=1&language=en&format=json`;
    
    const geoRes = await fetch(geoUrl);
    const geoData = await geoRes.json();

    if (!geoData.results || geoData.results.length === 0) {
      throw new Error(`Location '${destinationName}' not found`);
    }

    const { latitude, longitude, name, country, admin1 } = geoData.results[0];

    // 2. Weather Forecast
    const wxUrl = `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current_weather=true&hourly=relativehumidity_2m&daily=temperature_2m_max,temperature_2m_min&timezone=auto`;
    
    const wxRes = await fetch(wxUrl);
    const wxData = await wxRes.json();

    const cw = wxData.current_weather;
    const weatherInfo = WX_CODE_MAP[cw.weathercode] || { desc: 'Clear Weather', icon: '🌤️' };
    
    // Get humidity approximation from hourly if available
    const humidity = wxData.hourly?.relativehumidity_2m?.[0] || 65;
    const tempMax = wxData.daily?.temperature_2m_max?.[0] || Math.round(cw.temperature) + 4;
    const tempMin = wxData.daily?.temperature_2m_min?.[0] || Math.round(cw.temperature) - 4;

    return {
      success: true,
      place: `${name}${admin1 ? ', ' + admin1 : ''}, ${country || 'India'}`,
      temperature: Math.round(cw.temperature),
      tempMax: Math.round(tempMax),
      tempMin: Math.round(tempMin),
      feelsLike: Math.round(cw.temperature + (humidity > 70 ? 2 : 0)),
      windSpeed: Math.round(cw.windspeed),
      condition: weatherInfo.desc,
      icon: weatherInfo.icon,
      humidity,
      updatedAt: cw.time ? cw.time.replace('T', ' ') : 'Just now',
    };
  } catch (err) {
    return {
      success: false,
      error: err.message,
    };
  }
}
