from django.db import models
from datetime import date

class Verein(models.Model):

    mitgliedsbeitrag_cent = models.IntegerField()
    beschlussfassung      = models.DateField(default=date.today)

    def __str__(self):
        return (("Mitgliedsbeitrag: " + str(self.mitgliedsbeitrag_cent / 100.0)) if self.mitgliedsbeitrag_cent != None else "") + ", Beschlussfassung: " + str(self.beschlussfassung)

    class Meta:
        db_table = "verein"
        verbose_name = "Verein"
        verbose_name_plural = "Vereinsbeschlüsse"
