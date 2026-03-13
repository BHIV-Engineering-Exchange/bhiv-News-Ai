# 🌐 Production Connectivity Guide (Ngrok)

Since the backend services (Gateway, Core, Tools) are running on your local machine, deploying the Frontend to Vercel requires a way for Vercel servers to "talk back" to your `localhost`.

We use **Ngrok** to create secure tunnels.

## 1. Install Ngrok
Download from [ngrok.com](https://ngrok.com/download) and install.
Authenticate with your token:
```bash
ngrok config add-authtoken <YOUR_TOKEN>
```

## 2. Start Tunnels
We need to expose the **Gateway (Port 8000)** because it proxies requests to other services.

Run this command in a new terminal:
```bash
ngrok http 8000
```

## 3. Update Vercel Environment Variables
Once Ngrok starts, it will give you a public URL (e.g., `https://a1b2-c3d4.ngrok-free.app`).

Update your Vercel Project Settings -> Environment Variables:

| Variable | Value |
| :--- | :--- |
| `NEXT_PUBLIC_NOOPUR_API_BASE` | `https://<your-ngrok-id>.ngrok-free.app` |
| `NEXT_PUBLIC_SEEYA_API_BASE` | `https://<your-ngrok-id>.ngrok-free.app` |
| `NEXT_PUBLIC_SANKALP_API_BASE` | `https://<your-ngrok-id>.ngrok-free.app` |
| `NEXT_PUBLIC_AUDIO_BASE_URL` | `https://<your-ngrok-id>.ngrok-free.app/api/audio` |

## 4. Why this works
- The Frontend on Vercel sends requests to `https://...ngrok-free.app`.
- Ngrok forwards them to your local `localhost:8000` (FastAPI Gateway).
- The Gateway then talks to `localhost:3001` (Core) and `localhost:8001` (Tools) internally.
- **Result**: A live, public frontend controlling your local AI engine.

## ⚠️ Important Note
The free version of Ngrok changes the URL every time you restart it. For a permanent demo URL, keep the terminal open or upgrade to a paid plan.
