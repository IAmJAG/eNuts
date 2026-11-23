# DefaultFormatter / FileFormatter — Requirements, Rules, and Mental Model

Colored console formatter and plain file formatter for the jAGFx logging path.

**Location:** `src/jAGFx/logging/formatters/__defaultFormatter.py`  
**Setup:** `src/jAGFx/logging/__utilities.py` (`setupLogging`, `addFileHandler`)  
**Caller injection:** `src/jAGFx/logging/__log.py`

This document is the contract. Package-level notes live under `.docs/jAGFx/logging/`.

---

## 1. Purpose

Render log lines with a stable prefix of timestamp, level, domain, and member.

- `DefaultFormatter` — console only. Uses colorlog and ANSI. Never written to files.
- `FileFormatter` — file handlers only. Plain text, no ANSI. Skips empty lines.

`domain` is the class name when the call is inside a method, otherwise the module name. `member` is the function or method name. Both are display fields. Filtering uses `caller.fullyQualifiedName`, not these attributes.

---

## 2. Identity

| Fact | Rule |
|------|------|
| Console | `DefaultFormatter` + colorlog `ColoredFormatter` with `G_LOG_FORMAT` |
| File | `FileFormatter` with brace style `[{asctime}][{levelname:<8}] [{domain}] [{member}] {message}` |
| Domain source | `extra["domain"]` from project `log()`, or fallback from caller |
| Member source | `extra["member"]` from project `log()`, or fallback from caller |
| Fallback caller | `CallerInformation("", "NOT.MINE", None, None, None, -1)` when record has no caller |

---

## 3. Mental model

Project `log()` / `trace()` always inject `caller`, `domain`, and `member` via `extra=`.
Standard library and third-party records do not.

Both formatters must therefore ensure `domain` and `member` exist before the format string is applied. Missing attributes become:

- `domain` — `caller.klass` or `caller.module` or `"NOT.MINE"`
- `member` — `caller.member` or empty string

Without this, `%(domain)s` / `{domain}` raise `KeyError` inside the logging formatter and the module prints `--- Logging error ---`.

---

## 4. Requirements

### 4.1 Console (`DefaultFormatter`)

- Format must include timestamp, level, domain, member, and message.
- Colored via colorlog; ANSI is console-only.
- If `record.caller` is missing, set a `NOT.MINE` caller so `NamespaceFilter` can drop it.
- If `record.domain` or `record.member` is missing, set them from the caller (or `NOT.MINE` / empty).
- Empty or whitespace-only messages produce an empty string (handler skips write).
- Multi-line messages are formatted per non-empty line; continuation lines are indented with `TAB`.

### 4.2 File (`FileFormatter`)

- Same domain/member/caller rules as the console formatter.
- No ANSI.
- Empty results are not written.
- Trailing whitespace is stripped so the file does not grow blank lines.

### 4.3 Non-project records

- Records that never passed through project `log()` must not raise `KeyError` on `domain` or `member`.
- Fallback values must be stable and must not invent a real class or module name when none is known.

---

## 5. Acceptance

- Project TRACE lines keep the existing shape: `[timestamp][LEVEL] [domain] [member] message`.
- A `logging.warning` / third-party record that reaches the console or file handler formats without `KeyError: 'domain'`.
- `NOT.MINE` fallback records remain suppressible by `NamespaceFilter`.
