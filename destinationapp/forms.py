from django import forms
from .models import CustomUser, Country, State, District, Destination

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    country = forms.ModelChoiceField(queryset=Country.objects.all(), empty_label="Select Country")
    state = forms.ModelChoiceField(queryset=State.objects.none(), empty_label="Select State")
    district = forms.ModelChoiceField(queryset=District.objects.none(), empty_label="Select District")

    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'username', 'password', 'confirm_password', 'country', 'state', 'district']

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['state'].queryset = State.objects.filter(country_id=country_id)
            except (ValueError, TypeError):
                self.fields['state'].queryset = State.objects.none()

        if 'state' in self.data:
            try:
                state_id = int(self.data.get('state'))
                self.fields['district'].queryset = District.objects.filter(state_id=state_id)
            except (ValueError, TypeError):
                self.fields['district'].queryset = District.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")
        return cleaned_data

class DestinationForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = '__all__'

    Destination_img = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

