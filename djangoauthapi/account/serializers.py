from django.forms import ValidationError
from rest_framework import serializers
from account.models import User
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from account.utils import Util


# User Registration Serializer
class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'password2', 'tc']
        extra_kwargs ={
            'password':{'write_only':True}
        }

    # validating Password and Confirm Password while Registration
    def validate(self, attrs):
        password  = attrs.get('password')
        password2  = attrs.get('password2')

        if password != password2:
            raise serializers.ValidationError("Password and Password are not the same")
        
        return attrs
    
    def create(self, validate_data):
        return User.objects.create_user(**validate_data)
    
#****************************************************************************************************

# User Login Serializer
class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model  = User
        fields = ['email','password']


#****************************************************************************************************

# User Profile Serializer
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email','name']


#****************************************************************************************************

# User Change Password Serializer
class UserChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['password', 'password2']

    def validate(self,attrs):
        password  = attrs.get('password')
        password2  = attrs.get('password2')

        user =  self.context.get('user')

        if password != password2:
            raise serializers.ValidationError("Password and Password are not the same")

        user.set_password(password)
        user.save()
        return attrs


#****************************************************************************************************

# Send Password Reset Email Serializer
class SendPasswordResetEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = User
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            
            uid = urlsafe_base64_encode(force_bytes(user.id))
            print('Encoded uid', uid)

            token  = PasswordResetTokenGenerator().make_token(user)
            print('Password reset token', token)

            link = f"http://localhost:3000/api/user/reset/{uid}/{token}"
            print("Password reset link", link)

            # Send Email
            body = 'Click Following Link to Reset Your Password '+link
            data = {
                'subject': 'Reset Your Password',
                'body': body,
                'to_email': user.email
            }
            Util.send_email(data)

            return attrs

        else:
            raise ValidationError('You are not a Registered User')  


#****************************************************************************************************

# User Password Reset Serializer
class UserPasswordResetSerializer(serializers.ModelSerializer):  
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['password', 'password2']

    def validate(self,attrs):
        try:
            password  = attrs.get('password')
            password2  = attrs.get('password2')

            uid =  self.context.get('uid')
            token =  self.context.get('token')

            if password != password2:
                raise serializers.ValidationError("Password and Password are not the same")
            
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user,token):
                raise ValidationError("Token is not Valis or Expired")

            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise ValidationError("Token is not Valis or Expired")