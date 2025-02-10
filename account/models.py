from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class CustomUser(AbstractUser):
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]

    birth_date = models.DateField(null=True, blank=True, verbose_name="birthDay")
    profile_picture = models.ImageField(
        upload_to='profile_pics/', 
        blank=True, 
        null=True, 
        default='profile_pics/default-avatar.png', 
        verbose_name="Profile Picture"
    )
    bio = models.TextField(max_length=500, blank=True, verbose_name="Biografy")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True, verbose_name="Sex")
    modified_at = models.DateTimeField(auto_now=True, verbose_name="Modification Data")

    # Fixing the reverse accessor clash
    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

    def __str__(self):
        return self.username

    def get_profile_picture(self):
        """Returns the profile picture URL or a default if none exists."""
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return '/media/profile_pics/default-avatar.png'
