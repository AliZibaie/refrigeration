from django.db import models


class Refrigerant(models.Model):
    name = models.CharField(max_length=50, verbose_name="نام ماده مبرد")
    coolprop_name = models.CharField(max_length=50, verbose_name="نام در CoolProp")

    class Meta:
        verbose_name = "ماده مبرد"
        verbose_name_plural = "مواد مبرد"

    def __str__(self):
        return self.name


class Calculation(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام محاسبه")
    refrigerant = models.ForeignKey(Refrigerant, on_delete=models.CASCADE, verbose_name="ماده مبرد")
    t_evap = models.FloatField(verbose_name="دمای اواپراتور (°C)")
    t_cond = models.FloatField(verbose_name="دمای کندانسور (°C)")
    mass_flow = models.FloatField(verbose_name="نرخ جرمی (kg/s)")
    cop_ideal = models.FloatField(null=True, blank=True, verbose_name="COP ایده‌آل")
    cop_actual = models.FloatField(null=True, blank=True, verbose_name="COP واقعی")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "محاسبه"
        verbose_name_plural = "محاسبات"
        ordering = ['-created_at']

    def __str__(self):
        return self.name
