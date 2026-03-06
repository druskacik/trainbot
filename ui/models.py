from django.db import models

class Route(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    source = models.CharField(max_length=255)
    train_number = models.CharField(max_length=255)
    departure_station = models.CharField(max_length=255)
    arrival_station = models.CharField(max_length=255)
    travel_date = models.DateField()
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'routes'

    def __str__(self):
        return f"{self.departure_station} to {self.arrival_station} on {self.travel_date}"


class Price(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='prices')
    price = models.FloatField(null=True, blank=True)
    currency = models.CharField(max_length=3, null=True, blank=True)
    is_couchette = models.BooleanField(default=False)
    scraped_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'prices'

    def __str__(self):
        return f"{self.price} {self.currency} for {self.route_id}"
