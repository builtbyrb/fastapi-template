from locust import FastHttpUser, between, task


class HelloWorldUser(FastHttpUser):
    wait_time = between(1, 2)

    @task
    def hello_world(self) -> None:
        json = {
            "first_name": "string",
            "last_name": "string",
            "username": "string",
            "email": "user@example.com",
            "password": "barook74741A@",
        }

        self.client.post("users/register", json=json)
