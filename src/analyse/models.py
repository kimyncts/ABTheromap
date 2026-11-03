from django.db import models
from django.contrib.auth.models import User

class Analysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="analyses")
    name = models.CharField(max_length=200)
    description = models.TextField()
    coverage = models.IntegerField()
    e_value = models.FloatField()
    gaps = models.IntegerField()
    alignment_length = models.IntegerField()
    perc_identity = models.FloatField()
    seq_file = models.FileField(upload_to='files/Sanger')
    ngs_file = models.FileField(upload_to='files/NGS')
    start_time = models.DateTimeField(auto_now_add=True)
    is_processing = models.BooleanField(default=True)
    result = models.TextField(blank=True)


class BlastResult(models.Model):
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, related_name="blast_results")
    vh_or_vl = models.CharField(max_length=2, choices=[("VH", "VH"), ("VL", "VL")])
    qseqid = models.CharField(max_length=200)
    sseqid = models.CharField(max_length=200)
    pident = models.FloatField()
    length = models.IntegerField()
    mismatch = models.IntegerField()
    gapopen = models.IntegerField()
    qstart = models.IntegerField()
    qend = models.IntegerField()
    sstart = models.IntegerField()
    send = models.IntegerField()
    evalue = models.FloatField()
    bitscore = models.FloatField()
    qcovs = models.FloatField()
