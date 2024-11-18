from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


# Category Table
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
    ]

# Create your models here.
class Description(models.Model):
    book_name=models.CharField(max_length=100)
    edition=models.CharField(max_length=20)
    location=models.CharField(max_length=20)
    price=models.CharField(max_length=50)
    book_image=models.ImageField(upload_to='book_pic')
    phone=models.CharField(max_length=20,default='')
    seller=models.ForeignKey(User,on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=None, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')  # New field for status




    def __str__(self):
        return f"{self.book_name} - {self.category.name if self.category else 'Uncategorized'}"

    def get_absolute_url(self):
        return reverse('main:detail',kwargs={'pk':self.pk})




# Transaction Table
class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Description, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f'Transaction by {self.buyer.username} on {self.date}'



# Wishlist Table
class Wishlist(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Description, on_delete=models.CASCADE)
    

    def __str__(self):
        return f'Wishlist by {self.user.username}'


# Review Table
class Review(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()  # Rating could be a number between 1-5 or any scale you decide
    comment = models.TextField()
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)

    def __str__(self):
        return f'Review for {self.user.username} - Rating: {self.rating}'
