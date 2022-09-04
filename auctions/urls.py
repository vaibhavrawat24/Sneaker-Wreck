from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create",views.createListing,name="create"),
    path("displayCategory",views.displayCategory,name="displayCategory"),
    path("listing/<int:id>",views.listing,name="listing"),
    path("removeWatchList/<int:id>",views.removeWatchList,name="removeWatchList"),
    path("addWatchList/<int:id>",views.addWatchList,name="addWatchList"),
    path("watchList",views.displayWatchList,name="watchList"),
    path("addComment/<int:id>",views.addComment,name="addComment"),
    path("addBid/<int:id>",views.addBid,name="addBid"),
    path("closeAuction/<int:id>",views.closeAuction,name="closeAuction")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
