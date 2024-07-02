from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse_lazy
from django.views import View
from .forms import RegistrationForm, UserMediaForm
from .models import OtpToken,PersonalInfo,AdditionalInfo, UserMedia
from .forms import PersonalInfoForm,AdditionalInfoForm
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View, TemplateView, ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin



def index(request):
    if request.user.is_authenticated:
        user_media = UserMedia.objects.filter(user=request.user).first()
        # Your other logic here
        return render(request, 'index.html', {'user_media': user_media})
    else:
        return redirect('signin')

class ContactView(View):
    def get(self, request):
        return render(request, 'contact.html')

class AboutView(View):
    def get(self, request):
        return render(request, 'about.html')

def signup(request):
    form = RegistrationForm()  # Instantiate the form
    
    if request.method == "POST":
        form = RegistrationForm(request.POST)  # Bind POST data to the form instance
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! An OTP is sent to your email.')
            return redirect("verify-email", username=form.cleaned_data['username'])  # Redirect to verify-email URL
        # If form is not valid, continue rendering the signup form with errors
    
    # Context to be sent to the template
    context = {
        "form": form
    }
    
    return render(request, 'account/signup.html', context)
    
def verify_email(request, username):
    user = get_user_model().objects.get(username=username)
    user_otp = OtpToken.objects.filter(user=user).last()
    
    
    if request.method == 'POST':
        # valid token
        if user_otp.otp_code == request.POST['otp_code']:
            
            # checking for expired token
            if user_otp.otp_expires_at > timezone.now():
                user.is_active=True
                user.save()
                messages.success(request, "Account activated successfully!! You can Login.")
                return redirect("signin")
            
            # expired token
            else:
                messages.warning(request, "The OTP has expired, get a new OTP!")
                return redirect("verify-email", username=user.username)
        
        
        # invalid otp code
        else:
            messages.warning(request, "Invalid OTP entered, enter a valid OTP!")
            return redirect("verify-email", username=user.username)
        
    context = {}
    return render(request, "account/verify_token.html", context)

def resend_otp(request):
    if request.method == 'POST':
        user_email = request.POST["otp_email"]
        
        if get_user_model().objects.filter(email=user_email).exists():
            user = get_user_model().objects.get(email=user_email)
            otp = OtpToken.objects.create(user=user, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5))
            
            
            # email variables
            subject="Email Verification"
            message = f"""
                                Hi {user.username}, here is your OTP {otp.otp_code} 
                                it expires in 5 minute, use the url below to redirect back to the website
                                http://127.0.0.1:8000/verify-email/{user.username}
                                
                                """
            sender = "clintonmatics@gmail.com"
            receiver = [user.email, ]
        
        
            # send email
            send_mail(
                    subject,
                    message,
                    sender,
                    receiver,
                    fail_silently=False,
                )
            
            messages.success(request, "A new OTP has been sent to your email-address")
            return redirect("verify-email", username=user.username)

        else:
            messages.warning(request, "This email dosen't exist in the database")
            return redirect("resend-otp")
        
           
    context = {}
    return render(request, "account/resend_otp.html", context)


def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        print(f"Username: {username}, Password: {password}")  # Debug line
        
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            messages.success(request, f"Hi {request.user.username}, you are now logged-in")
            return redirect("index")
        else:
            messages.warning(request, "Invalid credentials")
            return redirect("signin")
    
    return render(request, "account/login.html")



# class LoginView(View):
#     def get(self, request):
#         return render(request, 'account/login.html')



class MatchingView(View):
    def get(self, request):
        return render(request, 'matching_page.html')

class TestView(View):
    def get(self, request):
        return render(request, 'test.html')
class TestView2(View):
    def get(self, request):
        return render(request, 'test2.html')

class CreateProfileView(View):
    def get(self, request):
        return render(request, 'create_profile.html')

class ProfileView(View):
    def get(self, request):
        # Dummy profile data
        profile = {
            "firstName": "John",
            "email": "john.doe@example.com",
            "birthday": "1990-01-01",
            "gender": "Male",
            "bio": "A short introduction about John.",
            "height": "180 cm",
            "weight": "75 kg",
            "status": "Single",
            "designation": "Software Engineer",
            "qualification": "B.Sc in Computer Science",
            "location": "New York, USA",
            "hobbies": "Reading, Traveling, Coding",
            "profilepic": "static/images/dp.jpg",  # You should place a sample image in your static folder and refer to it here
            "additional_images": [
                "static/images/lad1.jpg",
                "static/images/lad2.jpg",
                "static/images/lad3.jpg"
            ]
        }

        return render(request, 'profile.html', {'profile': profile})

class PlansView(View):
    def get(self, request):
        return render(request, 'plans.html')
    

class P_info_CreateView(LoginRequiredMixin, CreateView):
    model=PersonalInfo
    form_class =PersonalInfoForm
    template_name = 'profile/create_pinfo.html'
    success_url = reverse_lazy('index')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(P_info_CreateView, self).form_valid(form)


class A_info_CreateView(LoginRequiredMixin,CreateView):
    model=AdditionalInfo
    form_class=AdditionalInfoForm
    template_name='profile/create_ainfo.html'
    success_url=reverse_lazy('index')
    
    def form_valid(self, form):
        form.instance.user =self.request.user
        return super(A_info_CreateView,self).form_valid(form)
    
class UserMediaCreateView(LoginRequiredMixin,CreateView):
    model=UserMedia
    form_class=UserMediaForm
    template_name='profile/create_umedia.html'
    success_url=reverse_lazy('index')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(UserMediaCreateView,self).form_valid(form)
    
class UserMediaUpdateView(LoginRequiredMixin,CreateView):
    model=UserMedia
    form_class=UserMediaForm
    template_name='profile/update_umedia.html'
    success_url=reverse_lazy('index')
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(UserMediaUpdateView,self).form_valid(form)


class UserMediaUpdateView(LoginRequiredMixin, UpdateView):
    model = UserMedia
    form_class = UserMediaForm
    template_name = 'profile/update_umedia.html'
    success_url = reverse_lazy('index')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_media'] = get_object_or_404(UserMedia, user=self.request.user, pk=self.kwargs['pk'])
        return context
    
    