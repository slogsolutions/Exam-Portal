from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import QuestionUpload
from .services import import_questions_from_dicts, is_encrypted_dat, decrypt_dat_content
import pickle

@receiver(post_save, sender=QuestionUpload)
def import_on_upload(sender, instance, created, **kwargs):
    if not created:
        return
    
    try:
        # Read file content
        with instance.file.open('rb') as f:
            file_data = f.read()
        
        # File should already be validated as encrypted, but double-check
        if not is_encrypted_dat(file_data):
            print(f"❌ File {instance.file.name} is not encrypted. Rejecting.")
            return
        
        # Decrypt the file
        try:
            decrypted_data = decrypt_dat_content(file_data, instance.decryption_password)
            data = pickle.loads(decrypted_data)
            print(f"✅ Successfully decrypted {instance.file.name}")
        except ValueError as e:
            print(f"❌ Decryption failed for {instance.file.name}: {e}")
            return
        
        # Import the questions
        if isinstance(data, list):
            imported_count = len(import_questions_from_dicts(data))
            print(f"✅ Successfully imported {imported_count} questions from {instance.file.name}")
        else:
            print(f"❌ Invalid .dat structure: expected list of dicts")
            
    except Exception as e:
        print(f"❌ Error while importing from {instance.file.name}: {e}")