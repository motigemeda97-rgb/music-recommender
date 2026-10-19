
import { createClient } from "@supabase/supabase-js";
import type { FrontendRenderer } from "@streamlit/component-v2-lib";

interface AuthState {
  access_token: string;
  user_id: string;
  email: string;
  auth_event: string;
}

interface AuthData {
  supabase_url: string;
  supabase_anon_key: string;
}

const AuthComponent: FrontendRenderer<AuthState, AuthData> = ({
  data,
  parentElement,
  setStateValue,
}) => {
  parentElement.replaceChildren();

  const supabase = createClient(
    data.supabase_url,
    data.supabase_anon_key,
    {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: false,
      },
    },
  );

  // --------------------------------------------------
  // STYLING
  // --------------------------------------------------

  const style = document.createElement("style");

  style.textContent = `
    [hidden] {
      display: none !important;
    }

    .auth-card {
      box-sizing: border-box;
      width: 100%;
      max-width: 440px;
      margin: 12px auto;
      padding: 30px;
      border: 1px solid #41405f;
      border-radius: 22px;
      background: #171629;
      color: #f5f3ff;
      font-family: inherit;
      box-shadow: 0 12px 35px rgba(0, 0, 0, 0.35),
                  0 0 25px rgba(139, 92, 246, 0.10);
    }

    .auth-header {
      text-align: center;
      margin-bottom: 26px;
    }

    .auth-icon {
      width: 60px;
      height: 60px;
      display: grid;
      place-items: center;
      margin: 0 auto 16px;
      border: 1px solid #51418a;
      border-radius: 18px;
      background: #292044;
      font-size: 29px;
    }

    .auth-title {
      margin: 0 0 8px;
      color: #ffffff;
      font-size: 25px;
      line-height: 1.25;
      font-weight: 750;
      letter-spacing: -0.6px;
    }

    .auth-subtitle {
      margin: 0;
      color: #c4bfdc;
      font-size: 14px;
      line-height: 1.6;
    }

    .auth-form {
      display: grid;
      gap: 17px;
    }

    .auth-field {
      display: grid;
      gap: 8px;
    }

    .auth-label {
      color: #e8e4ff;
      font-size: 13px;
      font-weight: 650;
    }

    .auth-input {
      box-sizing: border-box;
      display: block;
      width: 100%;
      min-height: 48px;
      padding: 12px 14px;
      border: 1px solid #494660;
      border-radius: 11px;
      background-color: #222036 !important;
      color: #ffffff !important;
      -webkit-text-fill-color: #ffffff;
      font-family: inherit;
      font-size: 14px;
      color-scheme: dark;
      outline: none;
      transition: border-color 150ms, box-shadow 150ms;
    }

    .auth-input::placeholder {
      color: #a5a0bc !important;
      -webkit-text-fill-color: #a5a0bc;
      opacity: 1;
    }

    .auth-input:focus {
      background-color: #222036 !important;
      border-color: #a78bfa;
      box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.2);
    }

    .auth-input:disabled {
      opacity: 0.8;
      color: #d8d3eb !important;
    }

    .auth-input:-webkit-autofill,
    .auth-input:-webkit-autofill:hover,
    .auth-input:-webkit-autofill:focus {
      -webkit-text-fill-color: #ffffff !important;
      -webkit-box-shadow: 0 0 0 1000px #222036 inset !important;
      caret-color: #ffffff;
      border: 1px solid #a78bfa;
    }

    .auth-button {
      width: 100%;
      min-height: 49px;
      margin-top: 4px;
      padding: 12px 16px;
      border: 0;
      border-radius: 11px;
      background: linear-gradient(135deg, #8b5cf6, #6d4aff);
      color: #ffffff;
      font: inherit;
      font-size: 15px;
      font-weight: 700;
      cursor: pointer;
      transition: filter 150ms, transform 150ms;
    }

    .auth-button:hover:not(:disabled) {
      filter: brightness(1.15);
      transform: translateY(-1px);
    }

    .auth-button:disabled {
      opacity: 0.8;
      cursor: default;
    }

    .auth-mode-switch {
      display: flex;
      gap: 10px;
      margin-bottom: 4px;
    }

    .auth-mode-switch .auth-button {
      flex: 1;
      margin-top: 0;
    }

    .auth-status {
      min-height: 20px;
      margin: 17px 0 0;
      color: #d1cbe8;
      font-size: 13px;
      line-height: 1.6;
      overflow-wrap: anywhere;
    }

    .auth-status[data-kind="error"] {
      color: #fca5a5;
    }

    .auth-status[data-kind="success"] {
      color: #86efac;
    }

    .auth-status[data-kind="info"] {
      color: #c4bfdc;
    }

    .auth-footer {
      margin-top: 22px;
      padding-top: 16px;
      border-top: 1px solid #41405f;
      color: #aaa5c4;
      text-align: center;
      font-size: 12px;
    }

    .auth-signed-in-bar {
      display: flex;
      justify-content: flex-end;
      align-items: center;
      width: 100%;
      box-sizing: border-box;
      padding: 4px 0 12px;
    }

    .auth-signout-button {
      width: auto;
      min-width: 100px;
      min-height: 38px;
      margin: 0;
      padding: 8px 16px;
      border: 1px solid #51418a;
      border-radius: 10px;
      background: #292044;
      color: #ffffff;
      font: inherit;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
    }

    .auth-signout-button:hover:not(:disabled) {
      background: #403064;
    }

    .auth-signout-button:disabled {
      opacity: 0.7;
      cursor: default;
    }

    @media (max-width: 480px) {
      .auth-card {
        padding: 22px 18px;
        border-radius: 17px;
      }

      .auth-title {
        font-size: 23px;
      }
    }
  `;

  // --------------------------------------------------
  // BUILD THE AUTHENTICATION CARD
  // --------------------------------------------------

  const card = document.createElement("section");
  card.className = "auth-card";

  const header = document.createElement("header");
  header.className = "auth-header";

  const icon = document.createElement("div");
  icon.className = "auth-icon";
  icon.textContent = "🎵";
  icon.setAttribute("aria-hidden", "true");

  const heading = document.createElement("h2");
  heading.className = "auth-title";
  heading.textContent = "Welcome back";

  const subtitle = document.createElement("p");
  subtitle.className = "auth-subtitle";
  subtitle.textContent =
    "Sign in to discover music and save your favorite songs.";

  header.append(icon, heading, subtitle);

  const form = document.createElement("form");
  form.className = "auth-form";

  // Email field
  const emailField = document.createElement("div");
  emailField.className = "auth-field";

  const emailLabel = document.createElement("label");
  emailLabel.className = "auth-label";
  emailLabel.textContent = "Email address";
  emailLabel.htmlFor = "browser-auth-email";

  const emailInput = document.createElement("input");
  emailInput.className = "auth-input";
  emailInput.type = "email";
  emailInput.id = "browser-auth-email";
  emailInput.placeholder = "Enter your email address";
  emailInput.autocomplete = "email";
  emailInput.required = true;

  emailField.append(emailLabel, emailInput);

  // Password field
  const passwordField = document.createElement("div");
  passwordField.className = "auth-field";

  const passwordLabel = document.createElement("label");
  passwordLabel.className = "auth-label";
  passwordLabel.textContent = "Password";
  passwordLabel.htmlFor = "browser-auth-password";

  const passwordInput = document.createElement("input");
  passwordInput.className = "auth-input";
  passwordInput.type = "password";
  passwordInput.id = "browser-auth-password";
  passwordInput.placeholder = "Enter your password";
  passwordInput.autocomplete = "current-password";
  passwordInput.required = true;

  passwordField.append(passwordLabel, passwordInput);

  // Sign-in / Create Account mode switch
  const modeSwitch = document.createElement("div");
  modeSwitch.className = "auth-mode-switch";

  const signInModeButton = document.createElement("button");
  signInModeButton.type = "button";
  signInModeButton.textContent = "Sign In";
  signInModeButton.className = "auth-button";

  const createAccountModeButton = document.createElement("button");
  createAccountModeButton.type = "button";
  createAccountModeButton.textContent = "Create Account";
  createAccountModeButton.className = "auth-button";
  createAccountModeButton.style.background = "#292044";

  modeSwitch.append(signInModeButton, createAccountModeButton);

  // Submit button
  const signInButton = document.createElement("button");
  signInButton.className = "auth-button";
  signInButton.type = "submit";
  signInButton.textContent = "Sign In →";

  form.append(
    modeSwitch,
    emailField,
    passwordField,
    signInButton,
  );

  // Status message
  const status = document.createElement("p");
  status.className = "auth-status";
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  status.dataset.kind = "info";
  status.textContent = "Checking for a saved session...";

  // Footer
  const footer = document.createElement("footer");
  footer.className = "auth-footer";
  footer.textContent = "Your music journey continues here ♡";

  card.append(header, form, status, footer);

  // --------------------------------------------------
  // SIGN OUT BAR — SEPARATE FROM THE LOGIN FORM
  // --------------------------------------------------

  const signOutBar = document.createElement("div");
  signOutBar.className = "auth-signed-in-bar";
  signOutBar.hidden = true;

  const signOutButton = document.createElement("button");
  signOutButton.className = "auth-signout-button";
  signOutButton.type = "button";
  signOutButton.textContent = "Sign Out";

  signOutBar.append(signOutButton);

  parentElement.append(style, signOutBar, card);

  // --------------------------------------------------
  // ACCOUNT MODE
  // --------------------------------------------------

  let accountMode: "signin" | "signup" = "signin";
  let active = true;

  const setAccountMode = (mode: "signin" | "signup") => {
    accountMode = mode;

    const creatingAccount = mode === "signup";

    signInModeButton.style.background = creatingAccount
      ? "#292044"
      : "linear-gradient(135deg, #8b5cf6, #6d4aff)";

    createAccountModeButton.style.background = creatingAccount
      ? "linear-gradient(135deg, #8b5cf6, #6d4aff)"
      : "#292044";

    heading.textContent = creatingAccount
      ? "Create your account"
      : "Welcome back";

    subtitle.textContent = creatingAccount
      ? "Join us to discover and save your favorite music."
      : "Sign in to discover music and save your favorite songs.";

    signInButton.textContent = creatingAccount
      ? "Create Account →"
      : "Sign In →";

    passwordInput.autocomplete = creatingAccount
      ? "new-password"
      : "current-password";

    status.textContent = creatingAccount
      ? "Create an account to begin your music journey."
      : "Enter your details to sign in.";

    status.dataset.kind = "info";
  };

  signInModeButton.addEventListener("click", () => {
    setAccountMode("signin");
  });

  createAccountModeButton.addEventListener("click", () => {
    setAccountMode("signup");
  });

  setAccountMode("signin");

  // --------------------------------------------------
  // SHARE AUTHENTICATION STATE WITH STREAMLIT
  // --------------------------------------------------

  const publishAuthState = (
    session: {
      access_token: string;
      user: {
        id: string;
        email?: string;
      };
    } | null,
    event: string,
  ) => {
    if (!active) return;

    setStateValue("access_token", session?.access_token ?? "");
    setStateValue("user_id", session?.user.id ?? "");
    setStateValue("email", session?.user.email ?? "");
    setStateValue("auth_event", event);

    if (session) {
      // Signed in: hide the ENTIRE form card.
      card.hidden = true;
      signOutBar.hidden = false;

      signOutButton.disabled = false;
      signOutButton.textContent = "Sign Out";
    } else {
      // Signed out: show the form and hide Sign Out.
      card.hidden = false;
      signOutBar.hidden = true;

      emailInput.disabled = false;
      passwordInput.value = "";
      passwordInput.hidden = false;
      passwordLabel.hidden = false;
      modeSwitch.hidden = false;

      signInButton.hidden = false;
      signInButton.disabled = false;

      signInButton.textContent =
        accountMode === "signup"
          ? "Create Account →"
          : "Sign In →";

      if (event === "SIGNED_OUT") {
        emailInput.value = "";
        status.textContent = "You've signed out successfully.";
        status.dataset.kind = "success";
      } else {
        status.textContent = "Enter your details to sign in.";
        status.dataset.kind = "info";
      }
    }
  };

  // --------------------------------------------------
  // CHECK FOR AN EXISTING BROWSER SESSION
  // --------------------------------------------------

  const publishSession = async () => {
    try {
      const { data: sessionData, error } =
        await supabase.auth.getSession();

      if (!active) return;

      if (error) {
        status.textContent = "Could not check the saved session.";
        status.dataset.kind = "error";
        return;
      }

      publishAuthState(
        sessionData.session,
        sessionData.session ? "SIGNED_IN" : "SIGNED_OUT",
      );
    } catch {
      if (!active) return;

      status.textContent = "Could not check the saved session.";
      status.dataset.kind = "error";
    }
  };

  // --------------------------------------------------
  // SIGN IN / CREATE ACCOUNT
  // --------------------------------------------------

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (signInButton.disabled) return;

    const creatingAccount = accountMode === "signup";
    const email = emailInput.value.trim();
    const password = passwordInput.value;

    signInButton.disabled = true;
    signInButton.textContent = creatingAccount
      ? "Creating account..."
      : "Signing in...";

    status.textContent = creatingAccount
      ? "Creating your account..."
      : "Checking your account...";

    status.dataset.kind = "info";

    try {
      if (creatingAccount) {
        const { data: authData, error } =
          await supabase.auth.signUp({
            email,
            password,
          });

        if (!active) return;

        if (error) {
          status.textContent =
            `Account creation failed: ${error.message}`;
          status.dataset.kind = "error";
          return;
        }

        if (authData.session && authData.user) {
          publishAuthState(authData.session, "SIGNED_IN");
          passwordInput.value = "";
          return;
        }

        passwordInput.value = "";
        status.textContent =
          "Registration submitted! Check your email for a confirmation link, then sign in.";
        status.dataset.kind = "success";
      } else {
        const { data: authData, error } =
          await supabase.auth.signInWithPassword({
            email,
            password,
          });

        if (!active) return;

        if (error) {
          status.textContent =
            "Sign-in failed. Check your email and password, then try again.";
          status.dataset.kind = "error";
          return;
        }

        if (!authData.session || !authData.user) {
          status.textContent = "No login session was returned.";
          status.dataset.kind = "error";
          return;
        }

        publishAuthState(authData.session, "SIGNED_IN");
        passwordInput.value = "";
      }
    } catch {
      if (active) {
        status.textContent =
          "Something went wrong. Please try again.";
        status.dataset.kind = "error";
      }
    } finally {
      if (active && signOutBar.hidden) {
        signInButton.disabled = false;
        signInButton.textContent =
          accountMode === "signup"
            ? "Create Account →"
            : "Sign In →";
      }
    }
  });

  // --------------------------------------------------
  // SIGN OUT
  // --------------------------------------------------

  signOutButton.addEventListener("click", async () => {
    if (signOutButton.disabled) return;

    signOutButton.disabled = true;
    signOutButton.textContent = "Signing out...";

    try {
      const { error } = await supabase.auth.signOut();

      if (!active) return;

      if (error) {
        signOutButton.disabled = false;
        signOutButton.textContent = "Sign Out";
      }
      // The auth-state listener handles successful sign-out.
    } catch {
      if (!active) return;

      signOutButton.disabled = false;
      signOutButton.textContent = "Sign Out";
    }
  });

  // --------------------------------------------------
  // KEEP UI SYNCHRONIZED WITH SUPABASE
  // --------------------------------------------------

  const {
    data: { subscription },
  } = supabase.auth.onAuthStateChange((event, session) => {
    publishAuthState(session, event);
  });

  void publishSession();

  // Clean up when Streamlit removes the component.
  return () => {
    active = false;
    subscription.unsubscribe();
  };
};

export default AuthComponent;
