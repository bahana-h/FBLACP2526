# Google Places API Setup Guide

The Google Places API **works directly in your browser** - no backend proxy needed! 🎉

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click "Create Project" or select an existing project
4. Give it a name (e.g., "Business Boost")
5. Click "Create"

## Step 2: Enable Places API

1. In your project, go to **APIs & Services** > **Library**
2. Search for "Places API"
3. Click on **Places API**
4. Click **Enable**

## Step 3: Create API Key

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **API Key**
3. Your API key will be created
4. (Optional) Click "Restrict Key" to add restrictions:
   - **Application restrictions**: HTTP referrers
   - Add your website URL (e.g., `https://yourusername.github.io/*`)
   - **API restrictions**: Select "Restrict key" and choose "Places API"

## Step 4: Enter Your API Key

1. Open the website
2. Click "Enter Key" in the banner at the top
3. Paste your Google Places API Key
4. Click "Save"

## Step 5: Start Searching!

1. Enter a location (city, address, or zip code) OR
2. Click "Use My Location" to find businesses near you
3. Browse real local businesses!

## Pricing

- **Free Tier**: $200 free credit per month
- **Places API (Text Search)**: $32 per 1,000 requests
- With free credit: ~6,250 free searches per month
- After free credit: Pay-as-you-go pricing

**Note**: The free credit is usually more than enough for personal use!

## Why Google Places API?

✅ **Works directly in browser** - No backend needed!  
✅ **No CORS issues** - Designed for client-side use  
✅ **Rich data** - Ratings, reviews, photos, hours  
✅ **Reliable** - Google's infrastructure  
✅ **Free tier** - $200/month free credit  

## Troubleshooting

**"API key not valid" error:**
- Make sure you copied the entire API key
- Check that Places API is enabled in your project
- Verify your API key restrictions (if any)

**"This API project is not authorized" error:**
- Make sure Places API is enabled in your Google Cloud project
- Check that billing is enabled (free tier still requires billing account)

**"No businesses found":**
- Try a different location
- Make sure your location is specific (city name works best)
- Check that your API key has Places API enabled

**"Quota exceeded" error:**
- You've used up your free credit
- Check your usage in Google Cloud Console
- Consider upgrading your plan or waiting for next month's credit

## Alternative: Use Sample Data

If you don't want to set up an API key, the website will use sample businesses. You can still:
- Add your own businesses
- Leave reviews
- Save favorites
- Use all other features

## Need Help?

- [Google Places API Documentation](https://developers.google.com/maps/documentation/places/web-service)
- [Places API JavaScript SDK](https://developers.google.com/maps/documentation/places/web-service)
- [Google Cloud Console](https://console.cloud.google.com/)
