"""Google Photos source.

Google removed library-wide read access from its OAuth API in March 2025, so this
engine uses the photos.google.com web session instead: it reads the Google
cookies from a local Chrome started with --remote-debugging-port, lists the
library through the same RPC the web UI uses, and downloads a random daily set.

Nothing secret is written to disk: cookies are read from Chrome on every run.
"""
import datetime
import json
import os
import random
import re
import time

import requests
import websocket

PHOTOS = "https://photos.google.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36")
VIDEO_MARKER = "76647426"  # key present in item[9] only for videos
LIBRARY_FILE = "_library.json"
RECRAWL_DAYS = 30


class SessionError(Exception):
    """kind = 'chrome' (Chrome not reachable) or 'login' (Google rejected the session)."""

    def __init__(self, kind, message):
        super().__init__(message)
        self.kind = kind


class GooglePhotosEngine:
    def __init__(self, config_manager):
        self.config = config_manager

    # ---------- paths / settings ----------
    @property
    def folder(self):
        d = self.config.get('paths.google_photos_dir', 'GooglePhotosWallpapers')
        os.makedirs(d, exist_ok=True)
        return d

    def _cfg(self, key, default):
        return self.config.get(f'google_photos.{key}', default)

    def todays_images(self):
        prefix = datetime.date.today().strftime("%Y%m%d_")
        return sorted(os.path.join(self.folder, f) for f in os.listdir(self.folder)
                      if f.startswith(prefix) and f.lower().endswith('.jpg'))

    def needs_download(self):
        return len(self.todays_images()) < self._cfg('photos_per_day', 19)

    # ---------- session ----------
    def _chrome_cookies(self):
        port = self._cfg('chrome_debug_port', 9222)
        try:
            info = requests.get(f"http://127.0.0.1:{port}/json/version", timeout=5).json()
            ws = websocket.create_connection(info["webSocketDebuggerUrl"], timeout=10,
                                             suppress_origin=True)
            try:
                ws.send(json.dumps({"id": 1, "method": "Storage.getCookies"}))
                while True:
                    msg = json.loads(ws.recv())
                    if msg.get("id") == 1:
                        break
            finally:
                ws.close()
        except Exception:
            raise SessionError('chrome', "Chrome de NUCX no responde. Abrí Chrome (ClaudeChromeLaunch).")
        cookies = [c for c in msg.get("result", {}).get("cookies", [])
                   if c.get("domain", "").endswith(("google.com", "googleusercontent.com"))]
        if not any(c["name"] == "SID" for c in cookies):
            raise SessionError('login', "No hay sesión de Google en Chrome. Volvé a iniciar sesión en Google Fotos.")
        return cookies

    def _session(self):
        s = requests.Session()
        s.headers["User-Agent"] = UA
        for c in self._chrome_cookies():
            s.cookies.set(c["name"], c["value"], domain=c["domain"], path=c.get("path", "/"))
        return s

    def _tokens(self, s, account):
        r = s.get(f"{PHOTOS}/u/{account}/", timeout=30)
        found = {k: re.search(r'"%s":"([^"]+)"' % k, r.text) for k in ("SNlM0e", "cfb2h", "FdrFJe")}
        if "accounts.google.com" in r.url or not all(found.values()):
            raise SessionError('login', "Google pide iniciar sesión de nuevo. Volvé a entrar a Google Fotos en Chrome.")
        return {k: m.group(1) for k, m in found.items()}

    def _list_page(self, s, tk, account, page_token):
        req = json.dumps([[["lcxiM", json.dumps([page_token, None, None, None, 1]), None, "generic"]]])
        r = s.post(f"{PHOTOS}/u/{account}/_/PhotosUi/data/batchexecute",
                   params={"rpcids": "lcxiM", "source-path": f"/u/{account}/", "bl": tk["cfb2h"],
                           "f.sid": tk["FdrFJe"], "hl": "es", "rt": "c"},
                   data={"f.req": req, "at": tk["SNlM0e"]}, timeout=30)
        if r.status_code in (401, 403):
            raise SessionError('login', "Google rechazó la sesión. Volvé a iniciar sesión en Google Fotos.")
        for line in r.text.split("\n"):
            if line.startswith('[["wrb.fr"'):
                raw = json.loads(line)[0][2]
                d = json.loads(raw) if raw else []
                items = d[0] if d and isinstance(d[0], list) else []
                return items, (d[1] if len(d) > 1 else None)
        return [], None

    def _account(self, s):
        """Account index (/u/N/) that holds the library; auto-detected once."""
        acc = self._cfg('account_index', None)
        if acc is not None:
            return acc, self._tokens(s, acc)
        for n in range(6):
            try:
                tk = self._tokens(s, n)
            except SessionError:
                continue
            items, _ = self._list_page(s, tk, n, None)
            if items:
                self.config.set('google_photos.account_index', n)
                self.config.save()
                return n, tk
        raise SessionError('login', "No encontré tu biblioteca en ninguna cuenta de Chrome. Iniciá sesión en Google Fotos.")

    # ---------- library index ----------
    def _load_library(self):
        try:
            with open(os.path.join(self.folder, LIBRARY_FILE)) as f:
                return json.load(f)
        except Exception:
            return {"items": {}, "next": None, "complete": False, "crawled_at": None, "shown": []}

    def _save_library(self, lib):
        tmp = os.path.join(self.folder, LIBRARY_FILE + ".tmp")
        with open(tmp, "w") as f:
            json.dump(lib, f)
        os.replace(tmp, os.path.join(self.folder, LIBRARY_FILE))

    def _crawl(self, s, tk, account, lib):
        """Index up to N more pages per run so random picks cover the whole library."""
        if lib["complete"] and lib["crawled_at"]:
            age = (datetime.date.today() - datetime.date.fromisoformat(lib["crawled_at"])).days
            if age >= RECRAWL_DAYS:
                lib.update(items={}, next=None, complete=False)
        if lib["complete"]:
            return
        min_w = self._cfg('min_width', 1920)
        for _ in range(self._cfg('pages_per_run', 40)):
            items, nxt = self._list_page(s, tk, account, lib["next"])
            for it in items:
                try:
                    url, w, h = it[1][0], it[1][1], it[1][2]
                    is_video = VIDEO_MARKER in (it[9] or {})
                except (IndexError, TypeError):
                    continue
                if not is_video and w >= min_w and w > h:
                    lib["items"][it[0]] = url
            lib["next"] = nxt
            if not nxt:
                lib["complete"] = True
                lib["crawled_at"] = datetime.date.today().isoformat()
                break
            time.sleep(1)

    # ---------- daily set ----------
    def download_daily(self):
        """Download today's random set. Returns a result dict like DownloadEngine."""
        s = self._session()
        account, tk = self._account(s)
        lib = self._load_library()
        self._crawl(s, tk, account, lib)

        today = datetime.date.today().strftime("%Y%m%d")
        for f in os.listdir(self.folder):  # drop previous days
            if f.lower().endswith('.jpg') and not f.startswith(today + "_"):
                try:
                    os.remove(os.path.join(self.folder, f))
                except Exception:
                    pass

        want = self._cfg('photos_per_day', 19)
        have = self.todays_images()
        have_keys = {os.path.basename(p)[12:-4] for p in have}
        shown = set(lib.get("shown", []))
        pool = [k for k in lib["items"] if k not in shown and k[:24] not in have_keys]
        if len(pool) < want:  # everything shown once: start over
            shown = set()
            pool = [k for k in lib["items"] if k[:24] not in have_keys]
        random.shuffle(pool)

        got = len(have)
        session_checked = False
        for key in pool:
            if got >= want:
                break
            r = s.get(lib["items"][key] + "=w3840-h2160", timeout=30)
            if r.status_code in (401, 403) and not session_checked:
                self._tokens(s, account)  # raises SessionError('login') if the session died
                session_checked = True
            if r.status_code != 200 or not r.headers.get("Content-Type", "").startswith("image/"):
                lib["items"].pop(key, None)  # stale URL; it comes back on the next re-crawl
                continue
            with open(os.path.join(self.folder, f"{today}_{got:02d}_{key[:24]}.jpg"), "wb") as f:
                f.write(r.content)
            shown.add(key)
            got += 1

        lib["shown"] = list(shown)
        self._save_library(lib)
        if got == 0:
            return {'success': False, 'message': "Google Fotos no devolvió fotos utilizables."}
        return {'success': True, 'message': f"{got} fotos de Google Fotos para hoy.",
                'filename': f"{got} fotos", 'path': self.todays_images()[0]}
