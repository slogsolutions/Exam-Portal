from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import QuestionUpload
from .services import load_dat_from_filefield, import_questions_from_dicts

@receiver(post_save, sender=QuestionUpload)
def import_on_upload(sender, instance, created, **kwargs):
    if not created:
        return
    try:
        data = load_dat_from_filefield(instance.file)  # expects list[dict]
        if isinstance(data, list):
            import_questions_from_dicts(data)
        else:
            raise ValueError("Invalid .dat structure: expected list of dicts")
    except Exception as e:
        print(f"❌ Error while importing from {instance.file.name}: {e}")
