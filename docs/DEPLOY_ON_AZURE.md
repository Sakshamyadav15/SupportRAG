# SupportRAG - Detailed Azure Deployment Guide (Student Subscription)

This guide provides a comprehensive, step-by-step walkthrough to deploy the SupportRAG application (Frontend + Backend) to Microsoft Azure using the **Azure for Students** subscription. This approach uses the most cost-effective resources.

## Prerequisites

1.  **Microsoft Azure Account**: Ensure your "Azure for Students" subscription is active.
2.  **GitHub Account**: Required for seamless deployment integration.
3.  **Local Development Environment**: VS Code, Git installed.

---

## Part 1: Prepare the Project for Cloud Deployment

### 1.1 Update Frontend API URL
The frontend currently points to `localhost`. We need to make it dynamic or update it after backend deployment.
The easiest "no-fail" method is to set the API URL in the `frontend/.env` file or directly in the code, but for now, let's ensure it can be configured.

**Action**: Open `frontend/src/lib/api.ts` or where your API URL is defined.
Ensure it looks something like this (it likely defaults to localhost, which is fine for local dev, but we will override it):
```typescript
// Example location: frontend/src/lib/api.ts
export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
```
*Wait to change this until we have the real Backend URL.*

### 1.2 Verify Backend Configuration
Your `Dockerfile` in the root folder is already set up correctly to copying the code and installing dependencies.
**Crucial Note**: The `data/` folder (containing your FAISS vector stores) is being COPIED into the image by the `COPY . .` command. This means your initial data will be available in the cloud.
*Warning: If your app writes new data to disk, IT WILL BE LOST on restart. For a student demo, this "read-only" state is usually acceptable.*

---

## Part 2: Deploy the Backend (Azure Web App for Containers)

We will use **deployment from local source** or **GitHub Actions** to build the container. The simplest "student" path without complex registry setup is often **linking a GitHub repository**.

### Step 2.1: Push Code to GitHub
1.  Initialize git if not done: `git init`.
2.  Add all files: `git add .`
3.  Commit: `git commit -m "Ready for deployment"`
4.  Create a new repository on GitHub (e.g., `support-rag-azure`).
5.  Push your local code to this new GitHub repository.

### Step 2.2: Create the Web App
1.  Log in to the [Azure Portal](https://portal.azure.com).
2.  Search for **"App Services"** and click **Create** -> **Web App**.
3.  **Basics Tab**:
    *   **Subscription**: Azure for Students.
    *   **Resource Group**: Create new (e.g., `SupportRAG-RG`).
    *   **Name**: Unique name (e.g., `supportrag-backend-saksham`). *This will be your API URL: https://supportrag-backend-saksham.azurewebsites.net*
    *   **Publish**: Choose **Docker Container**.
    *   **Operating System**: **Linux**.
    *   **Region**: Choose one close to you (e.g., East US).
    *   **Pricing Plan**:
        *   Click "Change size" / "Explore pricing plans".
        *   Select **Basic B1** (Covered by student credit, reliable) or **Free F1** (Might be too weak for FAISS/ML libraries, try B1 first).
4.  **Docker Tab**:
    *   **Options**: Single Container.
    *   **Image Source**: **GitHub Actions** (This is the easiest automation).
    *   **GitHub account**: Authorize your account.
    *   **Organization/Repository**: Select your `SupportRAG` repo.
    *   **Branch**: `main`.
    *   **Dockerfile Location**: `Dockerfile` (It should auto-detect).
5.  **Review + Create**: Click Create. Azure will now create the resources.

### Step 2.3: Configure Environment Variables
1.  Go to your new Web App resource.
2.  Navigate to **Settings** -> **Environment variables**.
3.  Add the following (from your local `.env` or secrets):
    *   `GEMINI_API_KEY`: Your key.
    *   `OPENAI_API_KEY`: Your key.
    *   `ENVIRONMENT`: `production`
4.  Click **Apply** and then **Restart** the Web App.

### Step 2.4: Verify Backend
Wait for the GitHub Action to finish (check the "Actions" tab in your GitHub repo). Once green:
Visit `https://YOUR-APP-NAME.azurewebsites.net/docs`.
*   If you see the Swagger UI, the backend is LIVE!
*   **Copy this URL** (remove the slash at the end, e.g., `https://supportrag-backend.azurewebsites.net`).

---

## Part 3: Deploy the Frontend (Azure Static Web Apps)

### Step 3.1: Create Static Web App
1.  In Azure Portal, search for **"Static Web Apps"**.
2.  Click **Create**.
3.  **Basics Tab**:
    *   **Subscription**: Azure for Students.
    *   **Resource Group**: Select the same one (`SupportRAG-RG`).
    *   **Name**: `supportrag-frontend`.
    *   **Plan Type**: **Free** (Generous free tier for hobby/student projects).
    *   **Deployment details**: Select **GitHub**.
    *   **Organization/Repository/Branch**: Select your `SupportRAG` repo and `main` branch.
4.  **Build Details (Crucial)**:
    *   **Build Presets**: Select **React**.
    *   **App location**: `/frontend` (This is where your package.json lives).
    *   **Api location**: Leave empty (we are using a separate Python backend).
    *   **Output location**: `dist` (Standard Vite output).
5.  **Review + Create**: Click Create.

### Step 3.2: Configure Frontend Environment Variables
The frontend needs to know where the backend is.
1.  Go to your new Static Web App resource in Azure Portal.
2.  Navigate to **Settings** -> **Environment variables**.
3.  Add:
    *   `VITE_API_URL`: Paste your **Backend URL** from Step 2.4 (e.g., `https://supportrag-backend-saksham.azurewebsites.net`).
4.  Click **Apply**.

### Step 3.3: Re-trigger Build (Important)
Environment variables for Static Web Apps are injected at *build time*.
1.  Go to your GitHub Repository -> **Actions**.
2.  You will see a workflow running for "Azure Static Web Apps...".
3.  Cancel it if running, or wait for it to finish.
4.  To force a rebuild with the new variable:
    *   Make a small change to a frontend file (e.g., add a comment in `frontend/README.md`).
    *   Push to GitHub.
    *   Look at the Actions tab. A new build will start.
    *   Wait for it to complete.

---

## Part 4: Final Verification

1.  Open your Azure Static Web App URL (found in the "Overview" tab in Azure Portal).
2.  You should see your **Dark/Glass Theme** UI.
3.  The status indicator in the Sidebar/Dashboard (HealthPanel) should eventually turn **Green/Connected**.
4.  Try sending a message!

---

## Troubleshooting "Nothing Should Go Wrong"

*   **Backend "Application Error"**:
    *   Go to Web App -> **Log Stream**. It will show you exactly why Python crashed (usually missing API Key or memory issue).
    *   If memory issue (OOM): Upgrade App Service Plan to **B1** or **B2**.
*   **Frontend "Network Error"**:
    *   Check the Browser Console (F12).
    *   If you see CORS errors:
        *   Go to Backend Web App -> **CORS**.
        *   Add your **Frontend Static Web App URL** to the allowed origins list.
        *   Click Save.
*   **Vector Store Not Found**:
    *   Ensure your local `data/` folder was not in `.gitignore`.
    *   Check `Dockerfile` ensures `COPY . .` is executed (it is).

Enjoy your deployed RAG application!
