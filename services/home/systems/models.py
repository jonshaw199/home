from django.db import models

# Create your models here.
class System(models.Model):
    COMPUTER = 'computer'
    PHONE = 'phone'
    TV = 'tv'
    
    SYSTEM_TYPES = [
        (COMPUTER, 'Computer'),
        (PHONE, 'Phone'),
        (TV, 'TV'),
    ]
    
    name = models.CharField(max_length=100)
    system_type = models.CharField(max_length=20, choices=SYSTEM_TYPES)

    def __str__(self):
        return self.name
