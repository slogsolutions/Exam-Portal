from django import forms
from .models import QuestionUpload
from .services import is_encrypted_dat, decrypt_dat_content, load_questions_from_excel_data

class QuestionUploadForm(forms.ModelForm):
    decryption_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter decryption password',
            'class': 'form-control'
        }),
        help_text="Password required for encrypted DAT files"
    )

    class Meta:
        model = QuestionUpload
        fields = ["file", "decryption_password"]
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'})
        }

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get("file")
        password = cleaned_data.get("decryption_password")

        if file and password:
            try:
                # Read file content into memory
                file.seek(0)
                file_content = file.read()
                file.seek(0)  # Reset file pointer

                # Basic validation - check if it looks like encrypted data
                if not is_encrypted_dat(file_content):
                    raise forms.ValidationError(
                        "File does not appear to be encrypted. Expected encrypted DAT file."
                    )

                # Test decryption with provided password
                try:
                    decrypted_data = decrypt_dat_content(file_content, password)
                    
                    # Verify it's a valid Excel file by checking magic bytes
                    if not decrypted_data.startswith(b'PK'):
                        raise forms.ValidationError(
                            "Decrypted data is not a valid Excel file format."
                        )
                    
                    # Try to parse the Excel data to validate structure
                    try:
                        questions = load_questions_from_excel_data(decrypted_data)
                        if not questions:
                            raise forms.ValidationError(
                                "No valid questions found in the Excel file."
                            )
                        
                        # Store for later use in signals
                        cleaned_data['validated_questions_count'] = len(questions)
                        
                    except Exception as e:
                        raise forms.ValidationError(
                            f"Error parsing Excel structure: {str(e)}"
                        )
                        
                except ValueError as e:
                    raise forms.ValidationError(
                        f"Decryption failed: {str(e)}. Please check your password."
                    )
                
                # Store file content for later use
                cleaned_data['file_content'] = file_content
                
            except forms.ValidationError:
                raise  # Re-raise form validation errors
            except Exception as e:
                raise forms.ValidationError(
                    f"Error processing file: {str(e)}"
                )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set the password from form data
        if 'decryption_password' in self.cleaned_data:
            instance.decryption_password = self.cleaned_data['decryption_password']
        
        if commit:
            instance.save()
            
        return instance