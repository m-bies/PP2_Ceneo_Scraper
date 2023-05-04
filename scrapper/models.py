from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)
    ceneo_id = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')

    author = models.TextField(max_length=20, blank=True, null=True)
    rating = models.TextField(max_length=3)
    recommendation = models.TextField(max_length=15)
    confirmed = models.TextField(max_length=50)
    purchase_date = models.TextField(max_length=20)
    review_date = models.TextField(max_length=20)
    description = models.TextField(max_length=500)
    vote_up = models.IntegerField()
    vote_down = models.IntegerField()

    def __str__(self):
        
        author = self.author
        confirmed = self.confirmed
        purchase_date = self.purchase_date
        recommendation = self.recommendation
        rating = self.rating
        review_date = self.review_date
        description = self.description
        vote_up = self.vote_up
        vote_down = self.vote_down

        return f'{author} \n {confirmed} \n {purchase_date} \n {recommendation} \n {rating} \n {review_date} \n {description} \n {vote_up} \n {vote_down}'

class Advantages(models.Model):
    reviews = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='advantages')

    advantage = models.TextField(max_length=40, default='', blank=True, null=True)

class Disadvantages(models.Model):
    reviews = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='disadvantages')

    disadvantage = models.TextField(max_length=40, default='', blank=True, null=True)