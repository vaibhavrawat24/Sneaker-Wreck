from turtle import title
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import *

def listing(request,id):
    
    try:
        listingData=Listing.objects.get(pk=id)
    except Listing.DoesNotExist:
        listingData = None
        
    isListingInWatchList=request.user in listingData.watchlist.all()
    allComments=Comment.objects.filter(listing=listingData)
    isOwner=request.user.username==listingData.owner.username
    return render(request,"auctions/listing.html",{
        "listing": listingData,
        "isListingInWatchList":isListingInWatchList,
        "allComments":allComments,
        "isOwner": isOwner
    })
    
def closeAuction(request,id):
    try:
        listingData=Listing.objects.get(pk=id)
    except Listing.DoesNotExist:
        listingData = None
    listingData.isActive=False
    listingData.save()
    isListingInWatchList=request.user in listingData.watchlist.all()
    allComments=Comment.objects.filter(listing=listingData)
    isOwner=request.user.username==listingData.owner.username
    return render(request,"auctions/listing.html",{
        "listing": listingData,
        "isListingInWatchList":isListingInWatchList,
        "allComments":allComments,
        "isOwner": isOwner,
        "update":True,
        "message":"Your auction is closed"
    })
    
    
    
def addBid(request,id):
    newBid=request.POST['newBid']
    try:
        listingData=Listing.objects.get(pk=id)
    except Listing.DoesNotExist:
        listingData = None
    isListingInWatchList=request.user in listingData.watchlist.all()
    allComments=Comment.objects.filter(listing=listingData)
    isOwner=request.user.username==listingData.owner.username
    if int(newBid)>listingData.price.bid:
        updateBid=Bid(user=request.user,bid=int(newBid))
        updateBid.save()
        listingData.price=updateBid
        listingData.save()
        return render(request,"auctions/listing.html",{
            "listing": listingData,
            "message":"Bid was updated successfully",
            "update":True,
            "isListingInWatchList":isListingInWatchList,
            "isOwner": isOwner,
            "allComments":allComments
        })
    else:
        return render(request,"auctions/listing.html",{
            "listing": listingData,
            "message":"Bid update failed",
            "update":False,
            "isListingInWatchList":isListingInWatchList,
            "isOwner": isOwner,
            "allComments":allComments
        })
        
    
    
def addComment(request,id):
    currentUser=request.user
    try:
        listingData=Listing.objects.get(pk=id)
    except Listing.DoesNotExist:
        listingData = None
    message=request.POST['newComment']
    
    newComment=Comment(
        author=currentUser,
        listing=listingData,
        message=message
    )
    
    newComment.save()
    
    return HttpResponseRedirect(reverse("listing",args=(listingData.id, )))


def displayWatchList(request):
    currentUser=request.user
    listings=currentUser.listingWatchList.all()
    return render(request,"auctions/watchlist.html",{
        "listings":listings
    })
    
def removeWatchList(request,id):
    try:
        listingData=Listing.objects.get(pk=id)
    except Listing.DoesNotExist:
        listingData = None
        
    currentUser=request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing",args=(listingData.id, )))

def addWatchList(request,id):
    try:
        listingData=Listing.objects.get(pk=id)
    except Listing.DoesNotExist:
        listingData = None
        
    currentUser=request.user
    listingData.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing",args=(listingData.id, )))

def index(request):
    activeListings=Listing.objects.filter(isActive=True)
    allCategories=Category.objects.all()
    return render(request, "auctions/index.html",{
        "listings":activeListings,
        "categories": allCategories
    })
    
def displayCategory(request):
    if request.method=="POST":
        categoryFromForm=request.POST['category']
        
        try:
            category=Category.objects.get(categoryName=categoryFromForm)
        except Category.DoesNotExist:
            category = None
        activeListings=Listing.objects.filter(isActive=True,category=category)
        allCategories=Category.objects.all()
        return render(request, "auctions/index.html",{
            "listings":activeListings,
            "categories": allCategories
        })
    

def createListing(request):
    if request.method=="GET":
        allCategories=Category.objects.all()
        return render(request,"auctions/create.html",{
            "categories":allCategories
        })
    else:
        #getting data from form, checking the user, getting all content about category, creating a new listing object, inserting object in database, redirecting it to index page
        title=request.POST["title"]
        description=request.POST["description"]
        imageurl=request.POST["imageurl"]
        price=request.POST["price"]
        category=request.POST["category"]
        
        currentUser=request.user
               
        try:
            categoryData=Category.objects.get(categoryName=category)
        except Category.DoesNotExist:
            categoryData = None      
            
        bid=Bid(bid=float(price),user=currentUser)  
        bid.save()
        
        newListing=Listing(
            title=title,
            description=description,
            imageUrl=imageurl,
            price=bid,
            category=categoryData,
            owner=currentUser
        )
        
        newListing.save()
        
        return HttpResponseRedirect(reverse(index))


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
