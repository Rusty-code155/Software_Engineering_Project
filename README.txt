Transaction Manager Project Setup and Troubleshooting Guide

This guide provides step-by-step instructions for running the Transaction Manager project and highlights known bugs and errors as of April 27, 2025.
(Project should include: transaction tracker, dashboard, light and dark themes, wallet and account function for personal use, calander with appointments functionality.)
---

Step 1: Set Up the Environment
- Ensure you have Python 3.8 or higher installed on your system.
- The project uses a virtual environment. If you don't already have one set up, navigate to the project directory and create it:
  ```
  cd /path/to/Software_Engineering_Project/Phase_4
  python -m venv .venv
  ```
- Activate the virtual environment:
  - On Windows:
    ```
    .venv\Scripts\activate
    ```
  - On macOS/Linux:
    ```
    source .venv/bin/activate
    ```
- Install the required dependencies:
  ```
  pip install tkinter matplotlib
  ```
  Note: `tkinter` is usually included with Python, but if it's missing, you may need to install it separately (e.g., `sudo apt-get install python3-tk` on Ubuntu).

Step 2: Verify Project Files
- Ensure the following files are present in the Phase_4 directory:
  - GUI.py
  - log.py
  - stats.py
  - account.py
  - calendar_manager.py
  - wallet.py
- The project uses JSON files for data persistence (`transactions.json`, `account.json`, `wallet.json`, `appointments.json`). These will be created automatically if they don't exist.

Step 3: Run the Application
- With the virtual environment activated, run the main script:
  ```
  python GUI.py
  ```
  Alternatively, if you're using an IDE like VS Code, you can run it directly via the IDE's run button, ensuring the interpreter is set to the virtual environment's Python executable (e.g., `.venv\Scripts\python.exe` on Windows).

Step 4: Using the Application
- The application window should open with the Dashboard tab displayed.
- Navigate through tabs (Transactions, Account, Statistics, Calendar, Notifications, Wallet, Settings, Payment) using the sidebar.
- Key features:
  - Add/Edit/Delete transactions in the Transactions tab.
  - View statistics (charts) in the Statistics tab.
  - Manage planned payments and appointments in the Calendar tab.
  - Add/Remove payment methods in the Payment tab.
  - Add/Remove cards in the Wallet tab.
  - Switch themes (Light/Dark) in the Settings tab.

Step 5: Check Logs for Debugging
- The application logs debug information to `debug.log` in the project directory.
- If the application fails to start or behaves unexpectedly, check `debug.log` for error messages. Look for lines starting with "ERROR" or "WARNING".

---

Known Bugs and Errors

1. Application Hangs on Startup (KeyboardInterrupt)
   - Symptom: The application window doesn't open, and you need to press Ctrl+C to stop the script.
   - Cause: This can happen if one of the JSON files (`transactions.json`, `account.json`, etc.) is corrupted or improperly formatted.
   - Fix: 
     - Check `debug.log` for errors related to JSON parsing (e.g., "Error parsing transactions.json").
     - Open the problematic JSON file and ensure it's valid JSON. If it's corrupted, delete the file; the application will recreate it with default values.
     - Ensure no other process is locking the JSON files (e.g., close any text editor that might have the file open).

2. "No payment methods available" Error When Adding a Transaction
   - Symptom: When trying to add a transaction, you get an error: "Please select a payment method," but the dropdown is empty.
   - Cause: The application starts with no payment methods by default.
   - Fix: 
     - Go to the Payment tab and add at least one payment method (e.g., "Credit Card", "Cash").
     - Then return to the Transactions tab to add a transaction.

3. Statistics Tab Shows "No transaction data available"
   - Symptom: The Statistics tab displays "No transaction data available" for charts.
   - Cause: There are no transactions logged yet.
   - Fix: Add some transactions in the Transactions tab, then revisit the Statistics tab to see the charts.

4. Calendar Tab Doesn't Update After Adding a Planned Payment
   - Symptom: After adding a planned payment, the Calendar tab's overview doesn't reflect the new payment.
   - Cause: This could be a UI refresh issue.
   - Fix: Switch to another tab and back to the Calendar tab to force a refresh. The `update_calendar` method should then display the updated data.

5. File Permission Errors
   - Symptom: Error messages in `debug.log` like "Permission denied" when saving to JSON files.
   - Cause: The application doesn't have write permissions for the project directory.
   - Fix: 
     - Ensure the project directory has write permissions for your user.
     - On Windows, right-click the Phase_4 folder, go to Properties > Security, and grant full control to your user.
     - On macOS/Linux, use `chmod -R u+rw /path/to/Phase_4`.

6. Theme Not Applying Correctly
   - Symptom: After switching themes in the Settings tab, some UI elements retain the old theme's colors.
   - Cause: The `_update_widget_theme` method may not recursively update all widgets due to a recursion depth limit. (tried to fix this multiple times)
   - Fix: Increase the `max_depth` parameter in `_update_widget_theme` (e.g., from 10 to 20) if you have a deeply nested UI structure.

---

Troubleshooting Tips
- Always check `debug.log` for detailed error messages.
- If the application crashes, restart it after fixing the issue (e.g., corrupted JSON files).
- Ensure all dependencies are installed correctly.
- If a tab is unresponsive, switch to another tab and back to force a refresh.

If you experience any issues with the code, leave a comment on the GitHub page
Sincerely,
Turner Miles Peeples