# How to Deploy MdDoc Studio to Cloudflare Pages (100% Free Forever) 🌐🚀

You can deploy this web application to **Cloudflare Pages** in less than 2 minutes. It costs **$0.00 forever**, stays **online 24/7**, and handles **unlimited traffic** because all conversions run directly in the visitor's browser via WebAssembly (Pyodide).

---

## ⚡ Method 1: Git Integration (Recommended - Automatic Updates)

1. **Push this repository to GitHub**:
   ```bash
   git add .
   git commit -m "Add MdDoc Cloudflare Pages Web Studio"
   git push origin main
   ```

2. **Log in to [Cloudflare Dashboard](https://dash.cloudflare.com/)** (Free account).

3. Go to **Workers & Pages** → **Create application** → **Pages** → **Connect to Git**.

4. Select your **`MdDoc`** GitHub repository.

5. Configure Build Settings:
   - **Framework preset:** `None`
   - **Build command:** `python bundle_for_web.py` *(or leave blank)*
   - **Build output directory:** `web`

6. Click **Save and Deploy**.

🎉 **Your app is now live!** Cloudflare will provide a permanent global URL (e.g. `https://mddoc.pages.dev`).

---

## ⚡ Method 2: Direct Upload via Wrangler CLI (Instant Deploy without Git)

If you have Node.js / `npx` installed:

```bash
# 1. Ensure web bundle is built
python bundle_for_web.py

# 2. Deploy directly to Cloudflare Pages
npx wrangler pages deploy web --project-name=mddoc
```

---

## 🧪 Local Testing Before Deployment

You can test the Cloudflare Pages build locally anytime:

```bash
# Start local static server
python -m http.server 8080 --directory web
```
Then open: **`http://localhost:8080`** in your browser.

---

## 🔒 Why Cloudflare Pages is the Ideal Choice:
- **Zero Server Costs:** Cloudflare serves static assets; the user's browser converts the document.
- **Infinite Scalability:** 1 user or 1,000,000 users — server load is always 0%.
- **100% Data Privacy:** User documents never touch a remote backend server.
- **Free Custom Domain & SSL:** Link your own domain (e.g., `mddoc.com` or `docs.yourdomain.com`) with 1 click.
