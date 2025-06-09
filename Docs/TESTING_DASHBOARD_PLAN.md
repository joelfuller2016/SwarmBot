# Project Plan: Dynamic Testing Dashboard

This document outlines the tasks and subtasks for implementing the new testing dashboard feature. This plan is being tracked here due to a temporary technical limitation with the `taskmaster-ai` tool's handling of numeric IDs.

**Parent Task:** Implement Dynamic Testing Dashboard (Originally Task #40)

---

### Subtasks

- [x] **1. Setup Project Branch and File Structure**
  - **Description:** Create the `feature/dynamic-testing-dashboard` git branch and organize all analysis documents into their proper folders (`/Docs` and `/Docs/archive`).
  - **Status:** Done

- [x] **2. Develop Backend Test Runner Service**
  - **Description:** Create a new Python module (`src/core/test_runner_service.py`) responsible for discovering all `test_*.py` files, executing them using `pytest`, and capturing their output, status, and logs.
  - **Status:** Done

- [x] **3. Design and Implement Dashboard UI**
  - **Description:** Create a new Dash page layout (`src/ui/dash/pages/testing_dashboard.py`) with a clear table or grid to display test names, statuses (color-coded), and last-run times.
  - **Status:** Done

- [x] **4. Integrate Backend Service with UI**
  - **Description:** Develop the callback logic (in `src/ui/dash/callbacks/testing_callbacks.py`) to connect the dashboard UI to the backend service. This will use a `dcc.Interval` to periodically trigger the test runner and refresh the UI with new results.
  - **Status:** Done

- [ ] **5. Implement Dynamic Test Discovery in UI**
  - **Description:** Ensure that the test runner service automatically scans the `/tests` directory so that any new test file added to the project automatically appears on the dashboard without needing manual registration.
  - **Status:** Pending

- [ ] **6. Create Initial Unit Tests for the Dashboard**
  - **Description:** To follow best practices, create a basic test file to validate the new dashboard feature itself. This will also serve as the first test to appear on the new dashboard.
  - **Status:** Pending

- [ ] **7. Document the New Testing Dashboard Feature**
  - **Description:** Update the main `README.md` and any relevant UI documentation to explain how the new testing dashboard works and how to add new tests to be discovered.
  - **Status:** Pending