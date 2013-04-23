from google.appengine.ext import endpoints
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from endpoints_proto_datastore.ndb import EndpointsModel
from datetime import date, timedelta
import random


class User(EndpointsModel):
    displayName = ndb.StringProperty()
    email = ndb.StringProperty()
    password = ndb.StringProperty()
    dateJoined = ndb.DateProperty(auto_now_add=True)
    lastUpdated = ndb.DateProperty(auto_now=True)

class Ingredient(EndpointsModel):
    displayName = ndb.StringProperty()
    userEmail = ndb.StringProperty(required=True)
    quantity = ndb.FloatProperty()
    dateAdded = ndb.DateProperty(auto_now_add=True)
    upc = ndb.StringProperty()
    experationDate = ndb.DateProperty()

class IngredientList(EndpointsModel):
    userEmail = ndb.StringProperty()
    ingredients = ndb.StructuredProperty(Ingredient, repeated=True)


@endpoints.api(name='hungrynorse', version='v1',
               description='API for fridgeraider Management')
class FridgeraiderApi(remote.Service):
    @User.method(name='users.login',
                 path='users/{email}/{password}',
                 http_method='GET')
    def login(self, request):
        """
        This method takes a request that is the email and password
        for a user.  It then queries the data store and returns the 
        user object.
        """
        qo = ndb.QueryOptions(keys_only=True,limit = 1)
        qry  = User.query().filter(User.email==request.email).filter(User.password == request.password)
        print qry
        return qry.get()
    

    @User.method(name='users.register',
                 path='users/{displayName}/{email}/{password}',
                 http_method='POST')
    def register(self,request):
        """
        This method will take the users displayName, email, and password
        and returns the user object on success. Future work need to be done
        to encrypt the password and to make sure the email address is not 
        take.
        """
        user = User(displayName=request.displayName,
                      email = request.email,
                      password = request.password)
        user_key = user.put()
        print user_key
        user = user_key.get()
        return user

    @IngredientList.method(name='ingredient.list',
                 path='ingredient/{userEmail}',
                 http_method='GET')
    def listIngrediant(self,request):
        """
        This will return all ingrediants associated with a users Email
        """
        ingredients = []
        qry  = Ingredient.query().filter(Ingredient.userEmail==request.userEmail)
        print random.sample(qry,2)
        for ind in qry:
            ingredients.append(ind)
        return IngredientList(userEmail = request.userEmail,ingredients=ingredients)

    @User.method(name='users.isUser',
                 path='users/{email}',
                 http_method='GET')
    def isUser(self,request):
        """
        If user name is taken, it returns a user object with that email, 
        otherwise it returns a blank user object if in the user is free
        """
        qo = ndb.QueryOptions(keys_only=True)
        qry  = User.query().filter(User.email==request.email).count()
        print qry
        if qry!=0:
            return User(email=request.email)
        else:
            return User()



    @Ingredient.method(name='ingredients.add',
                 path='ingredients/{displayName}/{quantity}/{userEmail}',
                 http_method='GET')
    def addIngredient(self,request):
        """
        This method will add ingrediants in similar fashion to the User.
        It will also compute the experation data. It returns the Ingrediant object
        """
        ingred = Ingredient(displayName=request.displayName,
                      quantity = request.quantity,
                      userEmail = request.userEmail,
                      experationDate = date.today()+timedelta(days=14))
        ingred_key = ingred.put()
        print ingred_key
        ingred = ingred_key.get()
        return ingred

    @Ingredient.method(name='ingredients.remove',
                 path='ingredients/{displayName}/{userEmail}',
                 http_method='GET')
    def removeIngredient(self,request):
        """
        This method will remove an ingrediants. it will find the ingrediant
        based on user email and ingrediant name and remove it. Returns deleted ingrediant
        """
        qo = ndb.QueryOptions(keys_only=True,limit = 1)
        qry  = Ingredient.query().filter(Ingredient.userEmail==request.userEmail).filter(Ingredient.displayName == request.displayName)
        toRemove = qry.get()
        toRemove.key.delete()
        return toRemove

    @Ingredient.method(name='ingredients.updateQuantity',
                 path='ingredients/update/{displayName}/{userEmail}/{quantity}',
                 http_method='GET')
   
    def updateIngredientQuantity(self,request):
        """
        This method will replace the quantity stored with a new quantity. 
        It will then store the new one and return
        """
        qo = ndb.QueryOptions(keys_only=True,limit = 1)
        qry  = Ingredient.query().filter(Ingredient.userEmail==request.userEmail).filter(Ingredient.displayName == request.displayName)
        ind = qry.get()
        ind.quantity = request.quantity
        ind.put()
        return ind


application = endpoints.api_server([FridgeraiderApi])
