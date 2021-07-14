from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'username', 'email',
                  'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form__input'
        self.fields['first_name'].widget.attrs['class'] = 'form__input'
        self.fields['email'].widget.attrs['class'] = 'form__input'
        self.fields['password1'].widget.attrs['class'] = 'form__input'
        self.fields['password2'].widget.attrs['class'] = 'form__input'
