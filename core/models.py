from django.db import models
from django.contrib.auth.models import User

# Profile extends Django's built-in User with optional fields
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"

# Need represents a request from a person or group who needs help
class Need(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    amount_needed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    contact = models.CharField(max_length=200, blank=True)  # how to contact guardian or coordinator
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # optional image field for later extension
    image_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.title} ({self.amount_received}/{self.amount_needed})"

# Donation stores a donor contribution (we simulate payment and only record the donation)
class Donation(models.Model):
    need = models.ForeignKey(Need, related_name='donations', on_delete=models.CASCADE)
    donor_name = models.CharField(max_length=200)
    message = models.CharField(max_length=300, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor_name} -> {self.amount} to {self.need.title}"
