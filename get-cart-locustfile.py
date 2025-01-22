from locust import task, run_single_user, FastHttpUser
from insert_product import login


class AddToCartUser(FastHttpUser):
    host = "http://localhost:5000"
    username = "test123"
    password = "test123"
    token = None

    def on_start(self):
        """
        Initialize user session by logging in and retrieving the authentication token.
        """
        try:
            cookies = login(self.username, self.password)
            self.token = cookies.get("token")
            if not self.token:
                raise ValueError("Login failed. Token not received.")
        except Exception as e:
            self.environment.runner.quit()
            raise RuntimeError(f"Failed to initialize user: {e}")

    @task
    def view_cart(self):
        """
        Simulate viewing the cart.
        """
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "Cookie": f"token={self.token}",
            "Referer": f"{self.host}/product/1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Upgrade-Insecure-Requests": "1",
        }

        with self.client.get("/cart", headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to fetch cart. Status code: {response.status_code}")


if __name__ == "__main__":
    run_single_user(AddToCartUser)