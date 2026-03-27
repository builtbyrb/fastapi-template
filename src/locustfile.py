from locust import FastHttpUser, between, task


class HelloWorldUser(FastHttpUser):
    wait_time = between(0.1, 0.5)

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

        self.client.post("users/register", json=json)
