## 📝 How to add a new rule here?

If you wish to add a new convention to this file, please adhere to the following format to keep the documentation clear, structured, and easy to read. A single convention topic can contain multiple specific rules.

### [Convention Topic / Category Name]
*(Optional: A brief 1-2 sentence overview of this category)*

#### [Sub-rule 1: Name of the specific rule]
**Why:** [Explain the problem this rule solves or the value it brings in 1 sentence]
**Rule:** [Describe the exact convention to apply]

**❌ Bad:**
` ``python
Example of what NOT to do
` ``

**✅ Good:**
` ``python
Example of the expected code
` ``

## Pytest Naming Conventions
We rely on descriptive test names to quickly identify failures in CI/CD pipelines without needing to open the source code. Test names must form a complete, self-explanatory sentence.

#### 1. Standard Unit and Integration Tests
**Why:** To ensure any developer reading the test execution log immediately understands the action, the expected outcome, and the specific context of the scenario.
**Rule:** Test names must strictly follow the `test_<action>_<expected_result>_when_<condition>` pattern.

**❌ Bad:**
```python
def test_login(): ...
def test_user_email_validation(): ...
```

**✅ Good:**
```python
def test_login_user_returns_200_when_credentials_are_correct(): ...
def test_validate_email_returns_true_when_format_is_valid(): ...
```

#### 2. Parametrized Tests (`@pytest.mark.parametrize`)
**Why:** To prevent Pytest from generating unreadable test names (e.g., `test_health[True-expected1]`) when running multiple datasets through a single function.
**Rule:** The function name must describe the general action (`test_<action>_returns_expected_value`), and the `ids` parameter must explicitly define the specific conditions using the `["<result>_when_<condition>"]` format.

**❌ Bad:**
```python
@pytest.mark.parametrize("status", [False, True])
def test_health(status): ...
```

**✅ Good:**
```python
@pytest.mark.parametrize(
    ("status", "expected_value"), 
    [(False, "unhealthy"), (True, "healthy")],
    ids=["unhealthy_when_false", "healthy_when_true"]
)
def test_bool_to_health_returns_expected_value(status, expected_value): ...
```

#### 3. Testing Exceptions and Errors
**Why:** To clearly distinguish "happy path" tests from negative tests that ensure the system blocks invalid operations or fails gracefully.
**Rule:** Use the word `raises` (or `fails`) in the expected result segment of the test name: `test_<action>_raises_<exception_name>_when_<condition>`.

**❌ Bad:**
```python
def test_invalid_token_error(): ...
def test_create_user_duplicate(): ...
```

**✅ Good:**
```python
def test_decode_token_raises_invalid_token_exception_when_format_is_wrong(): ...
def test_create_user_returns_409_when_email_already_exists(): ...
```

#### 4. Parametrized Error Cases (`@pytest.mark.parametrize`)
**Why:** To test multiple invalid inputs that lead to exceptions without duplicating test logic, while ensuring the CI log clearly identifies exactly which negative scenario failed.
**Rule:** The function name must describe the general failure (`test_<action>_raises_expected_exception`), and the `ids` parameter must explicitly define both the exception and the condition using the `["raises_<exception>_when_<condition>"]` format.

**❌ Bad:**
```python
@pytest.mark.parametrize("invalid_payload", [{}, {"name": ""}])
def test_user_creation_errors(invalid_payload): ...
```

**✅ Good:**
```python
@pytest.mark.parametrize(
    ("invalid_payload", "expected_exception"), 
    [
        ({}, MissingFieldsError), 
        ({"name": ""}, EmptyNameError)
    ],
    ids=[
        "raises_missing_fields_error_when_payload_is_empty", 
        "raises_empty_name_error_when_name_is_blank"
    ]
)
def test_create_user_raises_expected_exception(invalid_payload, expected_exception): ...
```

#### 5. Testing Side Effects and State Changes
**Why:** Many functions do not return a specific value but instead change the state of the system (e.g., updating a database record, writing to a file, or triggering an external API call). The test name needs to reflect this state change rather than a return value.
**Rule:** Use verbs that describe the resulting state or action triggered in the expected result segment: `test_<action>_<state_change>_when_<condition>`.

**❌ Bad:**
```python
def test_user_activation(): ...
def test_payment_email(): ...
```

**✅ Good:**
```python
def test_activate_account_updates_db_status_to_active_when_token_is_valid(): ...
def test_process_order_sends_confirmation_email_when_payment_succeeds(): ...
```