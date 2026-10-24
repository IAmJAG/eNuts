# Requirements & Design Specifications

## 1. Project Overview
UI widgets specific to eNuts, including the recorder capture surface.

## 2. Functional Requirements
- **FR-1:** CaptureImage must behave as a normal Image when nothing is listening.
- **FR-2:** CaptureImage must emit keyboard and mouse events without embedding recording logic.

## 3. Non-Functional Requirements
- **NFR-1:** Remain a thin subclass of jAGQt Image.
