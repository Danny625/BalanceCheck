# One shared app without per-user model setup

The local app is working. Cloud deployment is a separate step and has not been performed.

## Local versus hosted configuration

Locally, `.env.local` stores the owner's key/model once and is deliberately ignored by Git. That file does not travel to GitHub or cloud hosting. The app reads it on later launches; users on that computer do not re-enter the key. Separate local clones need their own configuration.

For a single shared website, the deployment owner configures the hosted key/model once. Visitors use that configuration through the Python server. They do not receive the credential, select a model, or perform API setup. Their requests share the configured Google project's quota.

## Streamlit Community Cloud setup

1. Sign into Streamlit Community Cloud with the account that can deploy this private repository. Authorize the needed GitHub repository access.
2. Create an app from `Danny625/BalanceCheck`, branch `main`, entry point `app.py`. Use Python 3.14 to match the tested environment if available; otherwise verify installation/runtime with a supported Python version before sharing.
3. In deployment **Advanced settings → Secrets**, enter these two settings, replacing the placeholder privately:

```toml
GEMINI_API_KEY = "PASTE_PRIVATE_KEY_IN_STREAMLIT_ONLY"
GEMINI_MODEL = "gemini-3.5-flash-lite"
```

4. Leave `BALANCECHECK_LOCAL_SETUP` unset. Do not upload `.env.local`, use `Launch.command` as the hosted entry point, or commit secrets.
5. Deploy. Test the practice scenario in a new visitor session. Verify there is no key/model setup screen and that a report completes with evidence references.
6. Configure app sharing/access for the paired reviewers and test the link using a separate account/session before submission.

Streamlit keeps app secrets in the hosted app settings and exposes them server-side through `st.secrets`. They persist across visitor sessions and normal app restarts until the owner updates/removes them. See [official secrets instructions](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).

The software includes a hosted-secrets test confirming that configured credentials enable the Run button and hide owner setup controls. That test does not replace an actual cloud deployment/access check.

## Team access

The private personal GitHub repo is already shared with Scott and Elizabeth as write collaborators. That is sufficient for code collaboration. Owner-only repo settings are a GitHub personal-repo limitation; if all teammates later need GitHub Admin roles, use a team organization. GitHub collaborator access and Streamlit app/workspace management are separate permissions.
