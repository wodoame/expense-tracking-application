import { createClient } from '@supabase/supabase-js';

const supabaseUrl = (import.meta as any).env.VITE_PUBLIC_SUPABASE_URL; // Your Supabase project URL
const supabaseAnonKey = (import.meta as any).env.VITE_PUBLIC_SUPABASE_ANON_KEY; // Your Supabase public anon key

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function signUpWithGoogle() {
  localStorage.setItem('auth_action', 'signup');
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      // The redirectTo URL must be one of your Authorized redirect URIs configured in Google Cloud.
      // It's where Google will send the user back after successful authentication.
      // Often, this is your Supabase callback URL, or a specific route in your app
      // that handles the OAuth callback (e.g., /auth/callback).
      redirectTo: `${window.location.origin}/auth/callback`, // Example: redirects to a specific callback route in your app
    },
  });

  if (error) {
    console.error('Error signing in with Google:', error.message);
  } else if (data.url) {
    // If successful, Supabase returns a URL to redirect the user to Google's auth page
    window.location.href = data.url;
  }
}
async function signInWithGoogle() {
  localStorage.setItem('auth_action', 'signin');
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      // The redirectTo URL must be one of your Authorized redirect URIs configured in Google Cloud.
      // It's where Google will send the user back after successful authentication.
      // Often, this is your Supabase callback URL, or a specific route in your app
      // that handles the OAuth callback (e.g., /auth/callback).
      redirectTo: `${window.location.origin}/auth/callback`, // Example: redirects to a specific callback route in your app
    },
  });

  if (error) {
    console.error('Error signing in with Google:', error.message);
  } else if (data.url) {
    // If successful, Supabase returns a URL to redirect the user to Google's auth page
    window.location.href = data.url;
  }
}

async function getUser() {
  const { data: user } = await supabase.auth.getUser();
  return user?user:undefined;
}

window['signInWithGoogle'] = signInWithGoogle;
window['signUpWithGoogle'] = signUpWithGoogle;
window['getUser'] = getUser;