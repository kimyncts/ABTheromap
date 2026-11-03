from django.urls import path
from .views import index, login_user, logout_user, signup_user, historique_user, confirmation_logout

urlpatterns = [
    path ('', index, name="accounts-index"),
    path ('login/', login_user, name="accounts-login"),
    path ('logout/', logout_user, name="accounts-logout"),
    path ('signup/', signup_user, name="accounts-signup"),
    path ('historique/', historique_user, name="accounts-historique"),
    path ('confirmation/', confirmation_logout, name="accounts-confirmation")
]
