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
    status_updated_at = models.DateTimeField(null=True)
# {"cpu_usage": 3.6, "cpu_temperature": null, "memory_usage": 19.7, "disk_usage": 62.5, "network_sent": 1297, "network_received": 8838}
    cpu_usage = models.FloatField(null=True)
    cpu_temp = models.FloatField(null=True)
    mem_usage = models.FloatField(null=True)
    disk_usage = models.FloatField(null=True)
    network_sent = models.BigIntegerField(null=True)
    network_received = models.BigIntegerField(null=True)

    def __str__(self):
        return self.name
