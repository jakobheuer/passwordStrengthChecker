# Password Security Dashboard

A small password strength checker built with Python's standard libraries. Intuitive, real-time analysis of your password's security.

This was developed as a small side project, partly for fun and partly to explore how different Large Language Models (LLMs) can aid in the rapid development and iteration of such a tool—from generating initial code to refining UI concepts and writing documentation.

![Dashboard UI Screenshot](https://github.com/jakobheuer/passwordStrengthChecker/blob/main/UI.png)

---

### Project Goals

* **Visual & Intuitive:** Move away from simple text-based feedback to a graphical dashboard that gives an immediate sense of a password's strength.
* **Entropy-Based Analysis:** Calculate strength using **entropy**, which is a more accurate measure of unpredictability than just checking for length or character types.
* **Actionable Feedback:** Provide clear, immediate recommendations and show users *why* certain changes (like adding a new character type) are so effective.
* **Real-World Threat Simulation:** Integrate a feature to check passwords against user-provided wordlists (e.g., from known data breaches) to highlight the danger of using compromised credentials.
* **Standard Libraries Only:** Build the entire application using only the standard libraries that come with Python, requiring no external dependencies.

---

### Requirements

* **Python 3.x**
* No external libraries are needed.

* **(Optional but Recommended) A `wordlists` folder:**
    To enable the "Breach Check" feature, create a folder named `wordlists` in the same directory where you save the script. Place any `.txt` wordlist files inside this folder (e.g., `rockyou.txt`). The program will automatically detect them.

---

### How to Use

1.  **Download the Script:** Save the Python script (e.g., `passwordChecker.py`) to a folder on your computer.

2.  **Set up Wordlists (Optional):**
    * In the same folder you can copy Kali's standard `wordlists` folder. The programm will than also check if your Password is in one.
    * Download and place any `.txt` password lists into this folder.

3.  **Run the Application:**
    Open your terminal or command prompt, navigate to the folder containing the script, and run it:
    ```bash
    python password_dashboard.py
    ```

---

### Future Ideas

This project could be expanded with several new features:

* **Common Pattern Detection:** Add logic to detect and penalize common keyboard patterns (e.g., `qwerty`, `asdfg`), sequences (`abc`, `123`), and repeated characters (`aaabbb`).
* **UI Themes:** Add a simple toggle to switch between the current dark theme and a new light theme.
* **Secure Password Generator:** Include a feature to generate strong, random passwords based on user-selected criteria (length, character types), and ensure they don't appear in any loaded wordlists.
* **Animated Transitions:** Add subtle animations to the gauge needle and checklist for a smoother user experience.
