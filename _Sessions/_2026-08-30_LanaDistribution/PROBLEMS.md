# Session Problems

**Doc ID**: LANADIST-PROBLEMS

## Open

**LANADIST-PR-0001: PyApp first run takes 1-5 minutes (extraction + PyPI dependency install)**
- **History**: Added 2026-08-30 16:05 | Updated 2026-08-30 18:00 (measured: research 5-30 s claim covered extraction only)
- **Description**: First run extracts the embedded Python distribution, creates a venv, and installs openai/anthropic/pydantic from PyPI. Measured ~3-4 min. Network required.
- **Impact**: ACP clients may time out on first launch; users may think the binary hangs
- **Next Steps**: Documented in README (run once in terminal first). ACP handshake itself is safe (PR-0005 resolved). Wheelhouse embedding unsupported by PyApp - deferred.

**LANADIST-PR-0002: Code signing certificate not yet obtained**
- **History**: Added 2026-08-30 16:05
- **Description**: Windows Authenticode signing requires OV certificate (~100-200 EUR/year). Without it, SmartScreen blocks the binary.
- **Impact**: Users see "Windows protected your PC" warning. Corporate environments may quarantine.
- **Next Steps**: Evaluate Certum individual OV (~100 EUR) vs Azure Trusted Signing ($9.99/month). Budget and obtain certificate.

**LANADIST-PR-0003: Rust toolchain required for building**
- **History**: Added 2026-08-30 16:05 | Partially resolved 2026-08-30 18:00
- **Description**: PyApp builds via cargo. Build machine ALSO needs MSVC Build Tools (link.exe) - stable-gnu fails on missing dlltool.exe.
- **Impact**: ~4 GB one-time build machine setup (rustup + VS Build Tools VC workload)
- **Next Steps**: _build.ps1 offers rustup install; MSVC Build Tools documented. CI runner setup (PR-0004) must include both.

**LANADIST-PR-0004: No CI/CD pipeline yet**
- **History**: Added 2026-08-30 16:05
- **Description**: GitHub Actions workflow needed for automated builds on tag push. Must build per-platform (no cross-compilation).
- **Impact**: Manual builds are error-prone and not reproducible
- **Next Steps**: Create `.github/workflows/release.yml` after local `_ship.bat` works


**LANADIST-PR-0006: PyApp AV profile is assumed, not tested**
- **History**: Added 2026-08-30 16:15
- **Description**: Research labeled PyApp's low AV false-positive rate as [ASSUMED] (Rust binary, no bootloader pattern). No VirusTotal scan of an actual Lana PyApp binary exists.
- **Impact**: If assumption fails, AV quarantines undermine the main tool-choice rationale (LANADIST-DD-01)
- **Next Steps**: VirusTotal scan of first built binary. If flags exceed 2/71, evaluate PyInstaller --onedir fallback.

**LANADIST-PR-0007: Bundled prompt library needs privacy review before public release**
- **History**: Added 2026-08-30 16:40
- **Description**: `.lana/` skills (291 files, copied from personal DevSystem) may reference personal accounts, services, or identifying data (e.g. google-account, seo-tools configurations).
- **Impact**: Public distribution would leak personal context; violates Pre-Write Privacy Gate for shipped artifacts
- **Next Steps**: Full-text review of bundled library before first public release. Key-leak guard (IG-05) covers keys only, not general private data.


**LANADIST-PR-0009: Interrupted first run leaves a broken PyApp cache**
- **History**: Added 2026-08-30 17:35
- **Description**: Killing the binary during first-run dependency install leaves a venv without the lana package; every later start fails with 'No module named lana' (observed during TC pipeline test). PyApp does not self-heal.
- **Impact**: User who cancels the first run gets a permanently broken install
- **Next Steps**: Document recovery (`lana self restore` or delete `%LOCALAPPDATA%\pyapp\data\lana`) in README. Consider PYAPP option research for atomic installs later.

## Resolved

**LANADIST-PR-0005: PyApp first-run output may pollute ACP stdio handshake**
- **History**: Added 2026-08-30 16:10 | Resolved 2026-08-30 18:00
- **Solution**: Tested empirically (TC-10): fresh cache + `lana.exe --acp` + piped initialize -> stdout contained ONLY the 218-byte JSON-RPC response; all extraction output goes elsewhere. IDE-first-launch is safe (aside from 1-5 min delay, PR-0001).
- **Verification**: stdout/stderr captured separately via Start-Process redirection

**LANADIST-PR-0008: Latent bug - zero-setup never created model config files**
- **History**: Added 2026-08-30 16:40 | Resolved 2026-08-30 18:00
- **Solution**: FR-08 materialization (IMPL IS-03): missing model JSONs + key template written from bundle on default config path.
- **Verification**: TC-12 passes (pytest); TC-08 fresh-workspace binary run created all 7 artifacts and loaded 8 rules / 46 workflows / 23 skills

## Deferred

(none)

## Problems Changes

**[2026-08-30 18:00]**
- Resolved: LANADIST-PR-0005 (stdout pure on fresh-cache ACP start, TESTED)
- Resolved: LANADIST-PR-0008 (materialization implemented, TC-12/TC-08 pass)
- Updated: LANADIST-PR-0001 (first run measured 1-5 min incl. PyPI deps), LANADIST-PR-0003 (MSVC Build Tools also required)
- Added: LANADIST-PR-0009 (interrupted first run leaves broken cache)

**[2026-08-30 16:40]**
- Added: LANADIST-PR-0007 (bundled library privacy review)
- Added: LANADIST-PR-0008 (latent zero-setup bug: model JSONs never created)

**[2026-08-30 16:15]**
- Added: LANADIST-PR-0005 (ACP stdio pollution on first run)
- Added: LANADIST-PR-0006 (AV profile untested)

**[2026-08-30 16:05]**
- Added: LANADIST-PR-0001 (first-run penalty)
- Added: LANADIST-PR-0002 (code signing)
- Added: LANADIST-PR-0003 (Rust toolchain)
- Added: LANADIST-PR-0004 (CI/CD pipeline)
