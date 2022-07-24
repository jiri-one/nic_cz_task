from django.db import models

class Domain(models.Model):
    domain_name = models.CharField(max_length=200)
    registred = models.DateTimeField()
    unregistred = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.domain_name

class DomainFlag(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    expired = models.DateTimeField()
    outzone = models.DateTimeField()
    delete_candidate = models.BooleanField(default=False)

    def __str__(self):
        return self.domain
