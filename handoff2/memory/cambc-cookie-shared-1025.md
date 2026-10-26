---
name: cambc-cookie-shared-1025
description: USER 10-25 15:00 Madrid - every Claude session may use the site cookie (C:\Users\Javier\.cambc_cookie); only the loop session changes site state
metadata:
  type: feedback
---
USER 2026-10-25 ~15:00 Madrid: "que todos los claudes tengan acceso a esta cookie para que no haya que ir pidiéndosela los unos a los otros". Also: "la cookie da igual no me importa" (not worried about its exposure). This replaces the old rule that only the loop thread held the cookie.

**Why:** avoid sessions waiting on each other for site access.

**How to apply:** the cookie lives in `C:\Users\Javier\.cambc_cookie` (format `event_session=<64 hex>`, 78 bytes, saved by the user 14:58). Any session reads it via `session_cookie()` in `online/common.py` (repo clone `C:\Users\Javier\Cambc2026\thread\online\`). Never print it or copy it to another file, log, git or chat; never export this conversation's transcript to git (the user pasted the value once in chat). Coordinator's rule on top: only "Loop online en el PC" uploads versions, activates bots or launches challenges (avoids the duplicate-sender mess of 10-24); others use it read-only. Claude itself does not type the cookie into files; the user saves it. Related [[cambc-online-loop]], [[cambc-coordinator-here-1025]].
