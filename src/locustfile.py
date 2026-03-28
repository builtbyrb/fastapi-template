from locust import FastHttpUser, between, task


class HelloWorldUser(FastHttpUser):
    wait_time = between(1, 2)

    @task
    def hello_world(self) -> None:
        payload = {
            "grant_type": "password",
            "username": "user@example.com",
            "password": "barook74741A@",
        }
        json = {
            "first_name": "string",
            "last_name": "string",
            "username": "string",
            "email": "user@example.com",
            "password": "barook74741A@",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        }

        login_headers = {
            "ssq": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIyNzFhNGIxMi04M2QxLTQ0NWEtODUzYi1jNzhhN2MzMjdlOWUiLCJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzc0NjY0OTgzfQ.sAfvrOaTPO1ZMKk1iGJ4NCA2E1zYV8W-ksZPWzF2mqs"
        }

        self.client.post("users/profile", data=payload, headers=headers)
