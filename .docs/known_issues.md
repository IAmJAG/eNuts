# Component & UI Issues

### 1. Icon Animation Refactor (`StatefulIcon`)

* **Objective:** Decouple animation management from `StatefulIcon` to improve separation of concerns and component flexibility.
* **Requirements:**
  * Remove internal animation-building responsibilities from `StatefulIcon`.
  * Enable the component to optionally accept animation configuration options.
  * Construct the animation internally using the provided options.
  * Restrict `StatefulIcon`'s interaction with the animation strictly to triggering its start and end states.

---

### 2. Sidebar Menu: Ghost Button in Device Section

* **Issue Description:** A persistent "ghost" button remains visible in the Device section of the Sidebar Menu even after devices have been successfully added.
* **Root Cause Analysis:** Not sure of the cause, but it "might" come from the initial "no device" button created upon menu initialization.
* **Behavior:** 
  * **On Initial Load:** The ghost button visually renders when the window is first shown.
  * **On State Change:** The artifact automatically disappears once the sidebar's state is modified (e.g., toggled, collapsed, or expanded).