from django.db import models
from django.contrib.auth.models import User

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="liked_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')