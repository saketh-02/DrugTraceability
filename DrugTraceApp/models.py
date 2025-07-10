from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ethereum_address = models.CharField(max_length=42)  # Ethereum address is 42 chars including '0x'
    registration_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Product(models.Model):
    TRACE_STATUS_CHOICES = [
        ('Production', 'Production'),
        ('Processing', 'Processing'),
        ('Logistics', 'Logistics'),
        ('Sales', 'Sales'),
    ]

    name = models.CharField(max_length=200, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='products/')
    created_date = models.DateTimeField(default=timezone.now)
    last_update_date = models.DateTimeField(auto_now=True)
    current_status = models.CharField(max_length=20, choices=TRACE_STATUS_CHOICES, default='Production')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    blockchain_synced = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_date']

class TraceRecord(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='trace_records')
    trace_type = models.CharField(max_length=20, choices=Product.TRACE_STATUS_CHOICES)
    details = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    blockchain_tx_hash = models.CharField(max_length=66, blank=True, null=True)  # Ethereum tx hash is 66 chars including '0x'

    def __str__(self):
        return f"{self.product.name} - {self.trace_type} - {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']
