# Requirements & Design Specifications

## 1. Project Overview
Page is the standard host for application views inside the main window stack.

## 2. Functional Requirements
- **FR-1:** Page must expose title, description, and icon so callers can configure the header without touching Header directly.
- **FR-2:** Icon information must be optional at construction and fully settable afterward.
- **FR-3:** Header construction must not require icon layout details (position/size/colors); those are properties.

## 3. Non-Functional Requirements
- **NFR-1:** Keep `__init__` signatures short and stable for page builders.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Icon parameters moved out of Header.__init__
- **Affected Modules:** `jAGQt/widgets/header/__header.py`, `jAGQt/widgets/page/__page.py`
- **Description of Standard / Best Practice:** Some UI toolkits accept every visual option in the constructor.
- **Divergence:** Only `title`, `description`, and optional `icon` remain in constructors; layout and tinting are properties.
- **Design Decision & Justification:** Reduces call-site noise and matches the existing Title/Description property pattern used by Page.
- **Code Doc Cross-Reference:** See page.md and header.md.
