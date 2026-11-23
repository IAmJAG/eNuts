# Implementation Details

## 1. Architecture

```text
project log() / trace()
        │  extra={caller, domain, member, ...}
        ▼
QueueHandler → QueueListener
        ├─ DefaultFormatter (console, colorlog)
        └─ FileFormatter     (DateRotatingFileHandler)
```

Standard `logging.*` and third-party records enter the same path without `domain` / `member`.

## 2. Module map

| Source | Role |
|--------|------|
| `logging/formatters/__defaultFormatter.py` | `DefaultFormatter`, `FileFormatter` |
| `logging/__log.py` | Injects `caller`, `domain`, `member` into `extra` |
| `logging/__utilities.py` | Attaches console and file handlers |
| `logging/data/__callerInformation.py` | Caller FQN, klass, module, member |
| `logging/filters/__namespaceFilter.py` | Drops `NOT.MINE` and applies namespace levels |

## 3. Domain / member fallback

Both formatters, before applying the format string:

```python
if not hasattr(record, "domain"):
    setattr(record, "domain", getattr(caller, "klass", None) or getattr(caller, "module", "") or "NOT.MINE")
if not hasattr(record, "member"):
    setattr(record, "member", getattr(caller, "member", ""))
```

Caller is created as `CallerInformation("", "NOT.MINE", None, None, None, -1)` when missing.

## 4. Console format

`G_LOG_FORMAT` (percent style, colorlog):

```text
[asctime][levelname] [domain] [member] message
```

## 5. File format

Brace style default:

```text
[{asctime}][{levelname:<8}] [{domain}] [{member}] {message}
```

Empty formatted results are skipped by the handler. File output is stripped of trailing whitespace.
