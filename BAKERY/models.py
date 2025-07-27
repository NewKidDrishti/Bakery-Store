from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Product(models.Model):
    name= models.CharField(max_length=100)
    description = models.TextField(default='')
    img= models.ImageField(upload_to='products/', default='')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    offer= models.BooleanField(default=False)
    stock = models.PositiveIntegerField(default=0) # This is the new field

    def __str__(self):
        return self.name
    

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user or self.session_key}"
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"


