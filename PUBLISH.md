# Publishing LockIn to your phone — zero Git knowledge required

Everything below is copy-paste or double-click. (Understanding what these commands actually do
is a separate, optional thing — the app teaches it properly in **Learn → Cyber → Git School**.)

> Note: publishing only concerns the **mobile app** (this folder). The **LockIn Lab** desktop app
> in `Lab/` isn't published anywhere — it just runs locally on your PC (`Lab/Launch LockIn Lab.bat`).
> If you push this folder to GitHub, the `Lab/` folder rides along, which is fine.

## One-time setup (~10 minutes)

1. **Install Git** → <https://git-scm.com/download/win> (next-next-finish is fine).
2. **Create a GitHub account** → <https://github.com/signup> (free).
3. **Create the repository**: on GitHub press **+** (top right) → **New repository** →
   name: `lockin` → leave every checkbox OFF → **Create repository**.
   Copy the URL it shows, e.g. `https://github.com/YOURNAME/lockin.git`.
4. **Double-click `setup-github.bat`** in this folder and paste that URL when asked.
   (GitHub will pop up a login window the first time — sign in once and it's remembered.)
5. **Turn on the website**: on the repo page → **Settings** → **Pages** →
   Branch: `main`, folder `/ (root)` → **Save**.
   After ~1 minute your app is live at `https://YOURNAME.github.io/lockin/`.
6. **Install on the Redmi**: open that URL in **Chrome** on the phone → **⋮ → Add to Home
   screen / Install app**. Done — it works offline from now on.

If you'd rather type the commands yourself, this is everything `setup-github.bat` does:

```bash
git init
git branch -M main
git add -A
git commit -m "LockIn v1 - summer goal system app"
git remote add origin https://github.com/YOURNAME/lockin.git
git push -u origin main
```

## Every update afterwards (~10 seconds)

Double-click **`publish.bat`**. That's it. It runs:

```bash
git add -A
git commit -m "Update LockIn (<date time>)"
git push
```

Want a meaningful message instead of the timestamp? Run it from a terminal:

```bash
publish.bat Add new Hebrew vocab batch
```

### Ready-made commit messages (copy-paste)

| When you changed… | Use |
|---|---|
| First ever publish | `LockIn v1 - summer goal system app` |
| Vocab/flashcards | `Add new vocabulary and flashcards` |
| Workout program | `Tune workout program` |
| Daily schedule | `Adjust daily routine templates` |
| Bug fix | `Fix <what was broken>` |
| Anything visual | `Polish UI` |

## If something goes wrong

- **"git is not recognized"** → Git isn't installed (step 1), or reopen the terminal.
- **Push rejected / auth error** → a login window should appear; sign in to GitHub once.
- **Page shows old version on the phone** → close the app fully and reopen (the service
  worker updates itself on the next launch), or wait a minute — Pages can lag ~60s.
- **Broke everything locally?** → your published version is safe on GitHub. Worst case,
  download the repo zip from GitHub and start from that.
