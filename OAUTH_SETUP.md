# Google OAuth Setup Guide

This guide will help you set up Google OAuth authentication for your Garudaco application.

## Prerequisites

1. A Google Cloud Console account
2. A Google Cloud project (or create a new one)

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

## Step 2: Enable Google Sign-In API

1. In the Google Cloud Console, go to **APIs & Services** > **Library**
2. Search for "Google+ API" or "Google Sign-In API"
3. Click on it and press **Enable**

## Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. If prompted, configure the OAuth consent screen first:
   - Choose **External** user type (unless you have Google Workspace)
   - Fill in the required information:
     - App name: "Garudaco Learning Platform"
     - User support email: your email
     - App logo: optional
     - App domain: `http://localhost:3000`
     - Authorized domains: `localhost`
     - Developer contact: your email
   - Save and continue through the scopes (you can skip most)
   - Add test users if needed (your email address)

4. After OAuth consent screen is configured, create the OAuth client ID:
   - Application type: **Web application**
   - Name: "Garudaco Frontend"
   - Authorized JavaScript origins:
     - `http://localhost:3000`
     - `http://localhost` (if needed)
   - Authorized redirect URIs:
     - `http://localhost:3000`
     - `http://localhost:3000/login`

5. Click **Create**
6. Copy the **Client ID** (it looks like: `123456789-abcdefghijklmnop.apps.googleusercontent.com`)

## Step 4: Update Environment Variables

1. Open the `.env` file in the root directory of your project
2. Replace the placeholder values:

```bash
# Replace this line:
GOOGLE_CLIENT_ID=your-google-client-id-here.apps.googleusercontent.com
# With your actual client ID:
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com

# You can also update the JWT secret for better security:
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
```

3. Update the frontend `.env` file in the `frontend/` directory:

```bash
REACT_APP_GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
REACT_APP_API_URL=http://localhost:5000/api
```

## Step 5: Test the Setup

1. Start the application:
   ```bash
   docker-compose up --build
   ```

2. Open your browser and go to `http://localhost:3000`

3. You should see a login page with a Google Sign-In button

4. Click the Google Sign-In button and test the authentication flow

## Production Deployment

For production deployment, you'll need to:

1. Update the authorized origins and redirect URIs in Google Cloud Console to include your production domain
2. Update the environment variables with your production values
3. Ensure your OAuth consent screen is published (not in testing mode)

## Troubleshooting

### Common Issues

1. **"OAuth client not found"**: Check that your client ID is correct
2. **"Redirect URI mismatch"**: Ensure your redirect URIs in Google Cloud Console match exactly
3. **"This app isn't verified"**: This is normal for development. In production, you can submit for verification
4. **CORS errors**: Make sure your origins are properly configured in Google Cloud Console

### Test Mode vs Production

- In test mode, only specified test users can sign in
- To allow all users, you'll need to publish your OAuth consent screen
- You can have up to 100 test users before needing to publish

### Security Notes

- Never commit your actual Google Client ID to public repositories
- Use different client IDs for development and production
- Keep your JWT secret secure and change it in production
- Consider using environment-specific configuration files

## Support

If you encounter issues:
1. Check the browser console for error messages
2. Verify your Google Cloud Console configuration
3. Ensure all environment variables are set correctly
4. Check that the backend is running and accessible