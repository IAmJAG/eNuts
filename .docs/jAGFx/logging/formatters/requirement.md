# Requirements & Design Specifications

## 1. Project Overview

Console and file formatters for jAGFx logging. They render a stable prefix (timestamp, level, domain, member) and must tolerate records that did not come from the project `log()` helper.

## 2. Functional Requirements

- **FR-1:** Console output uses `DefaultFormatter` (colorlog / ANSI). File output uses `FileFormatter` (plain text).
- **FR-2:** Format includes `domain` (class if present, else module) and `member` (function/method).
- **FR-3:** Project `log()` / `trace()` inject `caller`, `domain`, and `member` via `extra=`.
- **FR-4:** If a record lacks `caller`, both formatters set a `NOT.MINE` `CallerInformation` so `NamespaceFilter` can drop it.
- **FR-5:** If a record lacks `domain` or `member`, both formatters set them from the caller (or `NOT.MINE` / empty). This prevents `KeyError` on standard and third-party records.
- **FR-6:** Empty or whitespace-only messages produce no written line.
- **FR-7:** Multi-line messages are emitted as one formatted line per non-empty source line.

## 3. Non-Functional Requirements

- **NFR-1:** File formatter never emits ANSI.
- **NFR-2:** Fallback values must not invent a real class or module name when the caller is unknown.
- **NFR-3:** Formatting must not raise on missing custom attributes.

## 4. Design Decisions

### Domain is display-only
`NamespaceFilter` uses `caller.fullyQualifiedName`, not the `domain` attribute. Removing or renaming `domain` in the format does not change filtering.

### Defensive setattr over format change
Keep the existing domain/member prefix. Guard both formatters so non-project records still format. This preserves current TRACE readability without KeyError.
