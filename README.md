# Gmail Email Processor

This project fetches emails from Gmail, processes them based on predefined rules, and saves the processed emails to a SQLite database.


## Installation

1.  **Prerequisites:**
    *   Python 3.x
    *   pip
    *   Google Cloud oauth configuration
    *   Necessary labels in Gmail if you want to move emails under a label

2.  **Install Required Packages:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Credentials:**
    *   Enable the Gmail API in the Google Cloud Console.
    *   Create a service account and download its JSON key file (e.g., `credentials.json`).  Save this file in a `config/` directory.
    *   Create an empty file named `token.json` in the `config/` directory. This file will store your authentication token.

4.  **Create Configuration File (`config/config.py`):**
    ```python
    DATABASE_FILE = "data/emails.db"
    RULES_FILE = "config/rules.json"
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    CREDENTIALS_FILE = "config/credentials.json"
    TOKEN_FILE = "config/token.json"
    LOGS_FILE = "logs/gmail_processor.log"
    ```
    Replace the placeholder values with your actual paths.

5.  **Create Rules File (`config/rules.json`):**  This file defines how emails will be processed.
    ```json
    [
      {
        "conditions": [
          {"field": "subject", "predicate": "Contains", "value": "important"},
          {"field": "received_date", "predicate": "greater than", "value": {"date": "2024-07-20", "unit": "days", "value": 0}}
        ],
        "predicate": "All",
        "actions": [
          {"action": "Move Message", "destination": "important"},
          {"action": "Mark as read"}
        ]
      }
    ]
    ```

    This example moves emails with "important" in the subject and received after July 20, 2024 to the "important" label and marks them as read.  See the included example `rules.json` for more comprehensive examples.

6.  **Run the Application:**
    - By default it fetches latest email only
    ```bash
    python main.py 
    ```
    - If you want to fetch multiple emails
    ```bash
    python main.py 5
    ```


## Database Schema (`emails` table)

The SQLite database will create a table named `emails` with these columns:

*   `id`: Unique Message ID (Primary Key, TEXT).
*   `sender`: Sender email address (TEXT).
*   `receiver`: Receiver email address (TEXT).
*   `subject`: Email subject (TEXT).
*   `message`: Email body (TEXT).
*   `received_date`: Email received date (DATETIME).
*   `status`: Email processing status (TEXT, e.g., 'read', 'unread').


# Summary of Rules in the Gmail Rule Engine

The Gmail Rule Engine is designed to process emails based on user-defined rules. Each rule consists of **conditions**, a **predicate**, and **actions**. The engine evaluates emails against these rules and executes the specified actions for matching rules.

## Types of Rules
### 1. **Conditions**
Conditions define the criteria an email must meet. Each condition includes:
- **Field**: The email attribute to evaluate (e.g., `received_date`, `subject`, `sender`).
- **Predicate**: The operation used to evaluate the condition (e.g., `Contains`, `Equals`, `Greater than`, `Less than`).
- **Value**: The value to compare the field against.

Examples of fields and their corresponding logic:
- **`received_date`**: Compares the email's received date using `less than` or `greater than` operators, with options to specify time units (e.g., `days`, `months`).
- **General Fields**: Evaluates attributes like `subject`, `sender`, or `body` using predicates such as `Contains`, `Does not contain`, `Equals`, and `Does not equal`.

### 2. **Predicates**
Predicates define the type of comparison between the email's field value and the specified condition value. Supported predicates:
- **`Contains`**: Checks if the field contains a substring.
- **`Does not Contain`**: Checks if the field does not contain a substring.
- **`Equals`**: Checks if the field exactly matches the value.
- **`Does not equal`**: Checks if the field does not match the value.
- **`Greater than`**: Checks if the field value is greater than the specified value (e.g., `received_date > 5 days`).
- **`Less than`**: Checks if the field value is less than the specified value (e.g., `received_date < 3 days`).

### 3. **Predicate Combination**
Rules can combine multiple conditions using the following predicates:
- **`All`**: All conditions must be true.
- **`Any`**: At least one condition must be true.

### 4. **Actions**
Actions define what should be done with the email when a rule matches. Supported actions include:
- **`Mark as read`**: Marks the email as read.
- **`Mark as unread`**: Marks the email as unread.
- **`Move Message`**: Moves the email to a specified folder or label.

---


### Sample examples 

-  [This rule ensures that any email received in the past 7 days without the word "Meeting" in the subject will be automatically moved to the "Notes" folder and marked as unread.](examples/example_1.md)
-  [This rule ensures that any email from "royalenfield" without the word "newsletter" in the subject will be automatically marked as read.](examples/example_2.md)

## Rule Processing Behavior
- **First Match**: Stops processing further rules after the first match (optional behavior controlled by `stop_after_first_match`).
- **Error Handling**: Logs warnings or errors if conditions are invalid or actions fail.

## Customization
Rules can be defined in a JSON file, allowing for easy modification of conditions and actions. The engine dynamically loads and processes these rules.


