# Requirements & Design Specifications

## 1. Project Overview
Device abstraction layer for fluxCore. Provides serializable identity and geometry that can be populated from ADB for SCRCPY sessions.

## 2. Functional Requirements
- **FR-1:** Device holds id, optional name, width, height and is Serializable.
- **FR-2:** SCRCPYDevice populates name and dimensions from ADB properties and window size.
- **FR-3:** Lazy property access triggers updateInfo when values are missing.

## 3. Non-Functional Requirements
- **NFR-1:** updateInfo failures are visible (warning or exception) rather than silent.
- **NFR-2:** Compatible with jAGFx serializer Properties list.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Lazy geometry population
- **Affected Modules:** `Device`, `SCRCPYDevice`
- **Divergence:** Properties call updateInfo on first access instead of requiring explicit call.
- **Design Decision & Justification:** Simplifies client code; discovery paths can create thin Device objects and hydrate later.
- **Code Doc Cross-Reference:** device.md, SCRCPYDevice.md.
