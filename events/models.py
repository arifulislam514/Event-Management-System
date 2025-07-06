from django.db import models


""" Participant Model """
class Participant(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name


""" Category M0del """
class Category(models.Model):
    name = models.CharField(max_length=70)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name


""" Event M0del """
class Event(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    time = models.TimeField()
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    participants = models.ManyToManyField(Participant,related_name='events',blank=True)
    
    def __str__(self):
        return self.name
    
    
""" Separate Location Model for Event """
class Location(models.Model):
    event = models.OneToOneField(Event,on_delete=models.CASCADE,related_name='location')
    country = models.CharField(max_length=65)
    city = models.CharField(max_length=65)
    
    def __str__(self):
        return f"{self.event.name} Location {self.country},{self.city}"
    
    
