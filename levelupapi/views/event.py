"""View module for handling requests about events"""
from django.core.exceptions import ValidationError
from rest_framework import status
#from django.http import HttpResponseServerError  NOT BEING USED YET
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from levelupapi.models import Event, Game, Gamer  
from django.contrib.auth.models import User  # remember- user is from django, it's not a model we made specifically for this program 



class EventView(ViewSet): #holds the functions to create, list, etc

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~ CREATE METHOD ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def create(self, request): #The create method holds 2 parameters: self and request
                               # If you look at the event model, you'll see we need to grab foreign keys from several objects to create a new event 
                               # We need to grab the logged in gamer to make an organizer, a game to make a game, 
        """Handle POST operations
        Returns: Response -- JSON serialized event instance
        """
        organizer = Gamer.objects.get(user=request.auth.user)#We need to grab the logged in user and store them as this event's organizer.
                                                             #Gamer is gamer model.  objects.get is an ORM.  .get is the ORM for grabbing a single item
                                                             #It will let us grab the user via their auth token.  
                                                             #Since we're using the gamer model, we have to import Gamer from levelupapi.models

         
        game = Game.objects.get(pk=request.data['gameId'])     # Next we need to grab the game object for the correct game (monopoly, etc).
                                                                # We use an ORM method on the Game model to grab the correct game object 
                                                                # For example, if it's a Risk event, grab the game object for Risk
                                                                # We do that by making pk equal to request.data, 
                                                                # That's because the field on request that gives us the body coming in from postman is the data field.
                                                                # Since data will be a dictionary type of state, we access the game id out of it with bracket notation
                                                                #We also need to make sure we import Game from levelupapi at the top of this file
        #Next we need a try and except section 
        #This section is where we try to create a new event object in our database.
        #Event.objects has a ORM used on it called .create that adds a new obj to the Events database
        #Inside create's parentheses, we put in all the fields we want in the object we're creating
        #It should match up to the properties in the Event model
        try:
            event = Event.objects.create(
                game=game,                  #game will be set to the variable we made above to grab the correct game
                organizer=organizer,        #organizer will be set to the variable we made above to grab the user creating the event  
                description=request.data['description'], #description will be pulled from the request data's (that's in dictionary form) description property
                date=request.data['date'], #date will be pulled from the request data's (that's in dictionary form) date property
                time=request.data['time'] #time will be pulled from the request data's (that's in dictionary form) time property
            ) 
            #Next we call the event serializer so we can return the created object to the front end
            #REMEMBER serializer turns it into JSON format so it can be sent to front end
            event_serializer = EventSerializer(event, context={'request': request}) #make a variable to hold invoking EventSerializer
                                                                                    #Note: code that does serializer logic is further down in this file
                                                                                    #Pass in 2 args- the object we tried to build, and needed info for the header
            return Response(event_serializer.data, status=status.HTTP_201_CREATED)  # The big return is the event and header info that's been serialized and the status code to confirm it was created
        except ValidationError as ex:   #catch any errors that occur diring the try process 
            return Response({'message': ex.args[0]}, status=status.HTTP_400_BAD_REQUEST) #The dictionary will have a 'message' key/property, and it's value will be ??????? and a 400 status message



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~ LIST METHOD ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def list(self, request):   # Now we need to define how to handle a GET for all events.  That means we use the 'list' method
                               # The list method holds 2 parameters: self and request

        """Handle GET operations for all events
        Returns: Response -- JSON serialized events
        """
        events = Event.objects.all() # Make a variable 'events' and grab all events from the database.
                                     # Event with uppercase E is the event Model.  
                                     # Event.objects means the objects in the database that match the Event model
                                     # .all() is an ORM that will grab all objects in the database that match the Event model
        
        events_serializer = EventSerializer(events, many=True) # Make a variable 'event_serializer' variable to hold a call for EventSerializer.
                                                               # For the arguments, pass in the events variable we just 
                                                               # made, many=True because 'events' will be a list of events, and the info we 
                                                               # need for the header (the context key:value pair)
        
        return Response(events_serializer.data)   # The return will be the data from the serialized list of events


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~ RETRIEVE METHOD ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   
    #The retrieve method is a lot like list, except retrieve will GET a single event. 

    def retrieve(self, request, pk):             # The retrieve method takes an extra argument - pk - because 
                                                # you are getting a single specific event

        event = Event.objects.get(pk=pk)         # Make a new variable called event.  Use the ORM .get method 
                                                # and pass the pk of the event you want into it.

        event_serializer = EventSerializer(event, context={'request': request}) # Make a new variable 'event_serializer'.  
                                                                                # In it, call the EventSerializer and pass in the event 
                                                                                # variable you just made and the context info for the headers

        return Response(event_serializer.data)   #return will be the result of the EventSerializer call inside event_serializer variable




#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~ DESTROY METHOD ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   
    # The destroy method looks similar to the retrieve method, except we're deleting a single event instead of 
    # getting and returning it.  That means we won't involve any serializers.

    def destroy(self, request, pk):             # The retrieve method takes an extra argument - pk - because 
                                                # you are getting a single specific event

        event = Event.objects.get(pk=pk)         # Make a new variable called event.  Use the ORM .get method 
                                                # and pass the pk of the event you want into it.

        event.delete()        #Call the delete() ORM on the event variable you just made
 
        return Response(None, status=status.HTTP_204_NO_CONTENT)   # Return will be the result of the .delete().  
                                 # 'None' refers to the data included in the return.  
                                 # status is the HTTP code that signals a successful deletion- '204 no content'





#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~ UPDATE METHOD ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   
    #The update method is a lot the retreive method because we are dealing with a single event

    def update(self, request, pk):             # The update method takes an extra argument - pk - because 
                                               # you are updating a single specific event

        event = Event.objects.get(pk=pk)        # Make a new variable called event.  Use the ORM .get method 
                                                # and pass the pk of the event you want into it.

        event.date = request.data['date']       # Now that we grabbed the correct event, we do our updates.
                                                # Here, we're updating the event's date.
                                                # We get the updated value for 'date' from the request.  
                                                # The request is in the data form of a dictionary so we need 
                                                # bracket notation to get to the 'date' key:value.
                                            
        event.time = request.time['time']                       # Here we're updating the time
        event.description = request.description['description']  # Here we're updating the description

        event.game = Game.objects.get(pk=request.data['gameId'])   # Here we're updating the game.  This one is trickier.
                                                                   # We have to grab the game object or we'll get an error
                                                                   # use the .get ORM on the Game model and pass the gameId from 
                                                                   # the update request into the ORM as the pk
        
        event.save()   # After we've done the changes above, we call the save method on the event

        return Response(None, status=status.HTTP_204_NO_CONTENT)   # Return will be the result of the .save().  
                                 # 'None' refers to the data included in the return.  
                                 # status is the HTTP code that signals a successful update- '204 no content'


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~ SERIALIZERS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#Now we define our needed serializers.  This section is tricky because we have to limit what information about the organizer aka user 
#is passed back to the front end.  We only want to pass the first and last name, not stuff like the user's password. To limit what gets passed 
#back, we build several serializers and call them inside of each other, AKA we make nested serializers.  
#The EventSerializer would pass back too much user info in the 'organizer' field, so we make a GamerSerializer that lets us serialize
#the user, then the UserSerializer lets us limit what gets serialized from the user field.
#Honestly it's a big rabbit hole of cause and effect
#Since the serializer code bounces around I numbered the steps in the order pieces are built


class UserSerializer(serializers.ModelSerializer):                # STEP_7: Define the new serializer Userserializer.  It's also a model serializer
    class Meta:
        model = User 
        fields = ('first_name', 'last_name')                      # STEP_8: Pull out just the first and last name.  Also, you'll need to import the user. You 
                                                                          #can go to models>gamer.py and copy the user import from the top
                                                                          #of it, then past it at the top of this file.  looks like 'from django.contrib.auth.models import User'


class GamerSerializer(serializers.ModelSerializer):              # STEP_4: Define the new serializer GamerSerializer.  It's also a model serializer
    
    user = UserSerializer()                                      # STEP_6: Make a new variable called user and call a new serializer called UserSerializer

    class Meta: 
        model = Gamer
        fields = ['user']                                        # STEP_5: at this point it would only pass the user id. We could  
        depth = 1                                                          #try to get more user info by doing 'depth = 1' but that
                                                                           #would pass back all user info, including passwords.  So we move to step 6 

class EventSerializer(serializers.ModelSerializer):              # STEP_1: define the EventSerializer class to hold all serializers.  The code in the 
                                                                 # parenthesis means that this will be a model serializer (that sounds weird- I mean it will serialize a model)

    organizer = GamerSerializer()                               # STEP_3: make variable called organizer (must match up with the field we are building a nested serializer for, in this 
                                                                        #case the 'organizer' field from class Meta).  Call a new serializer called GamerSerializer.
                
    class Meta:                                                  
        model = Event                                                          # STEP_2A: make the Meta class to hold the model and model fields
        fields = ['id', 'organizer', 'game', 'date', 'time', 'description']    # STEP_2B: We only want to pass back first/last name of organizer, which requires nested serializers, so we move to step 3      
        depth = 1                                                              # STEP_2C: Think of depth like JS expand.  Without it, a GET will only return the id number for the 'game' field.
                                                                                    # But depth one will return everything for the 'game' field (id, title, maker, num of players, skill level, game type, gamer) 
                                                                                    # The bigger the depth number, the more gets embedded.  If you set depth = 2, you'd get back gametype and gamer expanded.



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~ NEXT STEP NOT IN THIS FILE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # Now that you've made the EventView class, you have to add info from it into the urls.py file. You'll add:
                # router.register(r'events', EventView, 'event')

        # Then test your code with Postman to see if you can get events
                # Make sure your server is running (python3 manage.py runserver) a
                # In Postman, do a GET to http://localhost:8000/events and click 'send'
                # If the response in the body section (set it to JSON) is empty brackets, you don't have events in the database
                    # Add some by switching Postman to POST and setting the body to raw JSON.  URL stays the same as above.
                    # Build an event dictionary.  Here's a template to save time:
                      #  {
                      #      "gameId": 2,
                      #      "description": "This will be fun",
                      #      "date": "2021-12-03",
                      #      "time": "12:00:00"
                      #  }
                    # Click send and check for status 201 to confirm it was created.
                    # Try the GET again
