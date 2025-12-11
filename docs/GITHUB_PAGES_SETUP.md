# GitHub Pages Setup Guide

Your website is ready to deploy! Follow these steps:

## Step 1: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. Scroll down to **Pages** (left sidebar)
4. Under **Source**, select:
   - **Branch**: `main` (or your default branch)
   - **Folder**: `/docs`
5. Click **Save**

## Step 2: Wait for Deployment

- GitHub will automatically deploy your site
- It usually takes 1-2 minutes
- You'll see a green checkmark when it's done

## Step 3: Access Your Website

Your website will be available at:
```
https://YOUR_USERNAME.github.io/FBLACP2526/
```

Replace `YOUR_USERNAME` with your GitHub username.

## Troubleshooting

**"Deployment skipped" message:**
- Make sure you've set the Pages source to `/docs` folder
- Check that your `docs/index.html` file exists
- Wait a few minutes and refresh

**Build fails:**
- Check that all files in `docs/` are committed
- Make sure `docs/assets/app.js` and `docs/assets/styles.css` exist
- Check the Actions tab for error details

**Website shows 404:**
- Wait 5-10 minutes after enabling Pages (first deployment takes longer)
- Check that the URL matches your repository name exactly
- Make sure the repository is public (or you have GitHub Pro for private repos)

## Custom Domain (Optional)

If you want a custom domain:
1. Add a `CNAME` file in the `docs/` folder with your domain
2. Configure DNS settings with your domain provider
3. GitHub will automatically detect and use it

## Need Help?

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Pages Troubleshooting](https://docs.github.com/en/pages/getting-started-with-github-pages/troubleshooting-github-pages)

