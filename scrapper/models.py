from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    ceneo_id = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name
    
    def get_review_count(self):
        return self.reviews.count()
    
    def get_tolal_advantages(self):
        count = 0
        for review in self.reviews.all():
            count += review.advantages.count()
        return count
    
    def get_tolal_disadvantages(self):
        count = 0
        for review in self.reviews.all():
            count += review.disadvantages.count()
        return count
    
    def get_average(self):
        total_number = self.reviews.count()
        ratings = 0
        
        for review in self.reviews.all():
            ratings += int(review.rating[0:1])

        return round(float(ratings/total_number), 2) 
    
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

    def get_advantages_count(self):
        return self.advantages.count()

    def get_disadvantages_count(self):
        return self.disadvantages.count()
    
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
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='advantages')

    advantage = models.TextField(max_length=40)

class Disadvantages(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='disadvantages')

    disadvantage = models.TextField(max_length=40)