# Shree Annapure Foods — Instagram DM Auto-Responder

A lightweight FastAPI service that receives Instagram direct messages via Meta Webhooks, matches keywords, and sends predefined text and image replies. No database, no conversation history.

## Features

- Meta webhook verification and signature validation
- Keyword-based auto-responses (price, catalog, wholesale, location, greeting)
- Automatic image attachments from local static files
- Deployable to Render with environment variables only

## Project Structure

```
app/
  main.py              # FastAPI app, health endpoint, static files
  webhook.py           # GET/POST /webhook handlers
  instagram_service.py   # Meta Graph API messaging client
  keyword_engine.py    # Message normalization and rule matching
  config.py            # Environment configuration
  logger.py            # Logging setup
static/
  catalog.jpg
  wholesale.jpg
  price_list.jpg
requirements.txt
render.yaml
Dockerfile
.dockerignore
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `META_VERIFY_TOKEN` | Yes | Token for webhook verification (same as Meta App Dashboard) |
| `META_PAGE_ACCESS_TOKEN` | Yes | Page access token for sending messages |
| `META_APP_SECRET` | Yes | App secret for validating webhook signatures |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | Yes | Instagram Business Account ID (from webhook `entry.id`) |
| `PUBLIC_BASE_URL` | No | Public HTTPS URL for image attachments (defaults to `RENDER_EXTERNAL_URL` on Render) |
| `GRAPH_API_VERSION` | No | Meta Graph API version (default: `v22.0`) |

Copy `.env.example` to `.env` for local development:

```bash
cp .env.example .env
```

## Local Development

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Test the health endpoint:

```bash
curl http://localhost:8000/health
```

For webhook testing locally, expose your server with [ngrok](https://ngrok.com/) and use the ngrok HTTPS URL as your Meta callback URL.

## Meta App Setup

Follow the [Instagram Platform Webhooks documentation](https://developers.facebook.com/docs/instagram-platform/webhooks).

### 1. Create a Meta App

1. Go to [Meta for Developers](https://developers.facebook.com/) and create a **Business** app.
2. Add the **Instagram** product with **Instagram Messaging** (Messenger Platform).
3. Link your Facebook Page to your Instagram Professional account.

### 2. Required Permissions

- `instagram_basic`
- `instagram_manage_messages`
- `pages_manage_metadata`
- `pages_read_engagement`
- `pages_show_list`

Your app must be set to **Live** mode to receive production webhook notifications.

### 3. Configure Webhooks

In **App Dashboard → Webhooks**:

| Setting | Value |
|---|---|
| Callback URL | `https://<your-render-app>.onrender.com/webhook` |
| Verify Token | Same value as `META_VERIFY_TOKEN` |
| Object | Instagram |
| Field | `messages` |

Click **Verify and Save**.

### 4. Enable Page Subscriptions

Run once after deployment (replace placeholders):

```bash
curl -X POST "https://graph.facebook.com/v22.0/me/subscribed_apps?subscribed_fields=messages&access_token=<PAGE_ACCESS_TOKEN>"
```

Expected response:

```json
{"success": true}
```

### 5. Get Your Instagram Business Account ID

Send a test message to your Instagram account, then check Render logs for the webhook payload. The `entry[].id` field is your `INSTAGRAM_BUSINESS_ACCOUNT_ID`.

## Deploy to Render (Docker)

This project includes a [`Dockerfile`](Dockerfile) for containerized deployment on Render.

1. Push this repository to GitHub.
2. In [Render](https://render.com/), create a **New Web Service** from your repo.
3. Render detects `render.yaml` automatically (`runtime: docker`). Or configure manually:
   - **Environment:** Docker
   - **Dockerfile Path:** `./Dockerfile`
4. Add environment variables in the Render dashboard:
   - `META_VERIFY_TOKEN`
   - `META_PAGE_ACCESS_TOKEN`
   - `META_APP_SECRET`
   - `INSTAGRAM_BUSINESS_ACCOUNT_ID`
5. Deploy. Render sets `RENDER_EXTERNAL_URL` automatically for image URLs.

### Local Docker

```bash
docker build -t shree-annapure-bot .
docker run --rm -p 8000:8000 --env-file .env -e PORT=8000 shree-annapure-bot
```

Test: `curl http://localhost:8000/health`

### Replace Placeholder Images

Replace the files in `static/` with your real product images (JPEG, max 8MB each):

- `catalog.jpg` — product catalog
- `price_list.jpg` — price list
- `wholesale.jpg` — wholesale information

Images must be publicly accessible at `https://<your-app>.onrender.com/static/<filename>`.

## Response Rules

| Keywords | Response | Image |
|---|---|---|
| price, rate, cost, pricing, bhav, kitne ka | Price list message | `price_list.jpg` |
| catalog, menu, products, product list | Catalog message | `catalog.jpg` |
| wholesale, bulk, dealer, distributor, reseller | Wholesale message | `wholesale.jpg` |
| location, address, shop, store, where | Location message | — |
| hi, hello, hey, namaste | Greeting message | — |
| (no match) | Default message | — |

## Testing Checklist

1. **Health endpoint** — `curl https://<app>/health` returns `{"status":"ok"}`
2. **Webhook verification** — Meta Dashboard shows successful verification
3. **Price** — DM "price" → price text + `price_list.jpg`
4. **Catalog** — DM "catalog" → catalog text + `catalog.jpg`
5. **Wholesale** — DM "wholesale" → wholesale text + `wholesale.jpg`
6. **Location** — DM "location" → location text, no image
7. **Greeting** — DM "hello" → greeting text, no image
8. **Default** — DM unknown text → default text, no image
9. **Render deployment** — service is live and health check passes
10. **Logs** — webhook and API events visible in Render Logs tab

## Security Notes

- Webhook payloads are validated using `X-Hub-Signature-256` and your app secret.
- No customer data or conversation history is stored.
- Sender IDs may appear briefly in Render logs during processing.
- Never commit `.env` or expose tokens in code.

## API Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Deployment health check |
| GET | `/webhook` | Meta webhook verification |
| POST | `/webhook` | Receive Instagram messaging events |
| GET | `/static/*` | Serve product images for Meta attachments |

## References

- [Instagram Platform Webhooks](https://developers.facebook.com/docs/instagram-platform/webhooks)
- [Instagram Messaging — Send a Message](https://developers.facebook.com/docs/messenger-platform/instagram/features/send-message)
- [Instagram Messaging Webhooks](https://developers.facebook.com/docs/messenger-platform/instagram/features/webhook)
