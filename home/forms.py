from django import forms

class QuoteRequestForm(forms.Form):
    # --- Personal Data ---
    company = forms.CharField(required=False, max_length=200)
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(required=False, max_length=20)

    # --- Pickup Address ---
    pickup_street = forms.CharField(required=False, max_length=200)
    pickup_country = forms.CharField(required=False, max_length=100)
    pickup_city = forms.CharField(required=False, max_length=100)
    pickup_zip = forms.CharField(required=False, max_length=20)
    pickup_option = forms.ChoiceField(
        choices=[
            ("lift_gate", "Lift Gate at Pickup Point"),
            ("limited_access", "Limited Access Pickup"),
        ],
        widget=forms.RadioSelect
    )

    # --- Drop-Off Address ---
    drop_street = forms.CharField(required=False, max_length=200)
    drop_country = forms.CharField(required=False, max_length=100)
    drop_city = forms.CharField(required=False, max_length=100)
    drop_zip = forms.CharField(required=False, max_length=20)
    drop_option = forms.ChoiceField(
        choices=[
            ("call_before", "Call before Delivery"),
            ("lift_gate", "Lift Gate at Pickup Point"),
            ("limited_access", "Limited Access Pickup"),
            ("hazmat", "Hazmat"),
        ],
        widget=forms.RadioSelect
    )

    # --- Item To Be Shipped ---
    PACKAGING_CHOICES = [
        ("", "-- Select Packaging --"),
        ("box", "Box"),
        ("pallet", "Pallet"),
        ("crate", "Crate"),
        ("drum", "Drum"),
        ("bag", "Bag"),
        ("container", "Container"),
        ("roll", "Roll"),
    ]
    
    packaging = forms.ChoiceField(
        choices=PACKAGING_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    total_weight = forms.CharField(required=False, max_length=50)
    qty = forms.IntegerField(required=False)
    length = forms.CharField(required=False, max_length=50)
    width = forms.CharField(required=False, max_length=50)
    height = forms.CharField(required=False, max_length=50)
    stackable = forms.ChoiceField(
        choices=[
            ("stackable", "Stackable"),
            ("non_stackable", "Non-Stackable"),
        ],
        widget=forms.RadioSelect
    )
